from typing import Any
from simplibs.exception.testing import maybe_subtest
# Outers
from ...base_class import Rule


def assert_rule_is_valid(
    subtests: Any,
    rule: Rule,
    valid_values: list[Any],
    invalid_values: list[Any],
    *,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that rule.is_valid() and rule.__call__() satisfy the Boolean evaluation contract.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        rule: The Rule instance under test.
        valid_values: Values expected to satisfy the rule (True).
        invalid_values: Values expected to fail the rule (False), without raising.
        verbose: Enables isolated pytest subtest tracking for each checked value.
        intro: Optional prefix string added to generated subtest identity names.
    """
    assert isinstance(rule, Rule), (
        f"assert_rule_is_valid expects a Rule instance, got {type(rule).__name__}."
    )

    # 1. Verify positive values
    for index, val in enumerate(valid_values):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_is_valid_true_#index_{index}",
            verbose=verbose,
        ):
            assert rule.is_valid(val) is True, f"Expected is_valid({val!r}) to return True."

        with maybe_subtest(
            subtests,
            name=f"{intro}test_call_true_#index_{index}",
            verbose=verbose,
        ):
            assert rule(val) is True, f"Expected __call__({val!r}) to return True."

    # 2. Verify negative values (must evaluate to False without raising any exception)
    for index, val in enumerate(invalid_values):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_is_valid_false_#index_{index}",
            verbose=verbose,
        ):
            assert rule.is_valid(val) is False, f"Expected is_valid({val!r}) to return False."

        with maybe_subtest(
            subtests,
            name=f"{intro}test_call_false_#index_{index}",
            verbose=verbose,
        ):
            assert rule(val) is False, f"Expected __call__({val!r}) to return False."


_DESIGN_NOTES = """
# assert_rule_is_valid (Boolean Predicate Contract Blade)

## Purpose
Verifies the most fundamental contract every `Rule` subclass must honor:
`is_valid()` and the `__call__` shortcut must return strict booleans and
must never raise for values that are merely invalid (as opposed to
malformed in a way the rule cannot even evaluate — that boundary is the
job of `build_exception`, not `is_valid`).

---

## 1. Execution Rationale

* **Fail-Fast Type Guard:**
  Asserts `isinstance(rule, Rule)` before running anything else, so a
  misuse of this helper (passing a class instead of an instance, or an
  unrelated object) fails with an immediate, unambiguous message instead
  of a confusing `AttributeError` deep inside the loop.
* **Dual Interface Check:**
  Checks both `rule.is_valid(value)` and `rule(value)` for every value,
  since `Rule.__call__` is documented to delegate to `is_valid` — this
  guards against a subclass accidentally overriding one but not the other.
* **Strict Identity Comparison (`is True` / `is False`):**
  Uses `is` rather than truthiness so a rule that returns `1` or `0`
  instead of `True`/`False` fails the contract check, keeping the whole
  ecosystem's return-type guarantee strict.
"""
