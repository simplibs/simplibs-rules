from typing import Any
from simplibs.exception.testing import maybe_subtest
# Outers
from ...base_class import Rule


def assert_rule_describe(
    subtests: Any,
    rule: Rule,
    *,
    expected_text: str | None = None,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that rule.describe() satisfies the description contract.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        rule: The Rule instance under test.
        expected_text: If provided, rule.describe() must equal this text exactly.
        verbose: Enables isolated pytest subtest tracking for each check.
        intro: Optional prefix string added to generated subtest identity names.
    """
    assert isinstance(rule, Rule), (
        f"assert_rule_describe expects a Rule instance, got {type(rule).__name__}."
    )

    # 1. describe() must return a non-empty string and must never raise
    text: Any = None
    with maybe_subtest(
        subtests,
        name=f"{intro}test_describe_returns_text",
        verbose=verbose,
    ):
        text = rule.describe()
        assert isinstance(text, str) and text.strip() != "", (
            f"Expected describe() to return a non-empty str, got {text!r}."
        )

    # 2. Optional exact-text check
    if expected_text is not None:
        with maybe_subtest(
            subtests,
            name=f"{intro}test_describe_expected_text",
            verbose=verbose,
        ):
            assert text == expected_text, (
                f"Expected describe() == {expected_text!r}, got {text!r}."
            )


_DESIGN_NOTES = """
# assert_rule_describe (Description Contract Blade)

## Purpose
Verifies the `Rule.describe()` contract: it returns a non-empty `str` and
never raises. Optionally pins the exact text for a rule whose description
is part of its documented behavior.

---

## 1. Execution Rationale

* **Always Runs From assert_rule_contract:**
  Every rule inherits `describe()` with the class name as default, so the
  check passes for rules that have not (yet) overridden it. It only fails
  for a rule whose override is broken.
* **Exact Text Is Opt-In:**
  `expected_text` is rule-specific by nature (`"> 0"`, `"int | None"`), so it
  is supplied by the caller, mirroring how exact `problem` / `how_to_fix`
  wording is kept out of the generic contract.
* **Failure Isolation:**
  `text` is initialised before the first subtest, so a `describe()` that
  raises fails the first subtest and the second one reports a clear
  mismatch instead of a `NameError`.
"""
