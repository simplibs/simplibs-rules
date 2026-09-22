from typing import Any
from simplibs.exception.testing import maybe_subtest
# Outers
from ...tools import raise_invalid
from ...base_class import Rule


def assert_rule_raise_invalid(
    subtests: Any,
    rule: Rule,
    invalid_values: list[Any],
    *,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that the standalone raise_invalid() function raises for a Rule the same way build_exception() would.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        rule: The Rule instance under test.
        invalid_values: Values expected to trigger raise_invalid() unconditionally.
        verbose: Enables isolated pytest subtest tracking for each checked value.
        intro: Optional prefix string added to generated subtest identity names.
    """

    for index, val in enumerate(invalid_values):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_raise_invalid_#index_{index}",
            verbose=verbose,
        ):
            expected_exc = rule.build_exception(val)

            raised: BaseException | None = None
            try:
                raise_invalid(val, rule)
            except BaseException as exc:  # noqa: BLE001 — capturing to compare type below
                raised = exc

            assert raised is not None, (
                f"raise_invalid(value={val!r}, rule) did not raise, "
                f"expected {type(expected_exc).__name__}."
            )
            assert type(raised) is type(expected_exc), (
                f"raise_invalid(value={val!r}, rule) raised {type(raised).__name__}, "
                f"expected {type(expected_exc).__name__} (matching rule.build_exception())."
            )


_DESIGN_NOTES = """
# assert_rule_raise_invalid (Unconditional Raise Contract Blade)

## Purpose
Verifies the standalone `raise_invalid()` function — the "condition
already checked, just raise" counterpart to `validate()` — for a given
`Rule` instance. Nothing else in this testing toolkit previously exercised
`raise_invalid()`.

---

## 1. Execution Rationale

* **Type-Equivalence Contract:**
  `raise_invalid()` and `Rule.build_exception()` are guaranteed by design
  to construct the exception the same way when the rule branch is taken
  (`raise_invalid` literally calls `rule.build_exception(...)` internally
  for `Rule` instances — see its own design notes). This blade asserts
  that guarantee holds by comparing the *type* of what `raise_invalid`
  actually raises against a freshly built reference exception from
  `rule.build_exception(val)`.
* **Why Type, Not Full Field Equality:**
  Two independently constructed exception instances for the same `val`
  are expected to carry equal diagnostic content, but stack-trace-derived
  fields (`caller_info`) will legitimately differ between the two call
  sites. Comparing `type(...)` keeps this check meaningful without
  becoming a brittle, unintended assertion on stack location.
* **No Value/Value-Name Echo Assertions:**
  Unlike `assert_rule_build_exception`, this helper calls `raise_invalid`
  with no `value_name`/`context`, since its only job is to confirm the
  unconditional raise path is wired correctly for this rule — full field
  content is already exhaustively covered by `assert_rule_build_exception`.

---

## 2. Placement in the Contract

Optional in `assert_rule_contract` (only run when the caller wants it),
since `raise_invalid` is a thin, generic dispatcher shared by every rule
in the ecosystem — most contract runs won't need to re-verify it per
rule, but it remains available for thoroughness.
"""
