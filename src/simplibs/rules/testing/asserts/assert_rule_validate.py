from typing import Any
from simplibs.exception.testing import assert_function_valid_input, assert_function_raises
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


def assert_rule_validate(
    subtests: Any,
    rule: Rule,
    valid_values: list[Any],
    invalid_values: list[Any],
    *,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that rule.validate() behaves correctly across all operational modes.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        rule: The Rule instance under test.
        valid_values: Values expected to pass validate() in both standard
            and return_value=True modes.
        invalid_values: Values expected to raise ValidationError in standard
            mode, and to return False in return_bool=True mode.
        verbose: Enables isolated pytest subtest tracking for each checked value.
        intro: Optional prefix string added to generated subtest identity names.
    """

    def check_valid(value: Any) -> None:
        assert rule.validate(value) is True
        assert rule.validate(value, return_value=True) == val

    def check_return_bool_false(value: Any) -> None:
        assert rule.validate(value, return_bool=True) is False

    # 1. Positive checks (pass without exception, in both return modes)
    for index, val in enumerate(valid_values):
        assert_function_valid_input(
            subtests,
            check_valid,
            valid_params=(val,),
            verbose=verbose,
            intro=f"{intro}test_validate_pass_#index_{index}_",
        )

    # 2. Negative checks (raise ValidationError in standard mode; return False in return_bool mode)
    for index, val in enumerate(invalid_values):
        assert_function_raises(
            subtests,
            rule.validate,
            invalid_params=(val,),
            exception_type=ValidationError,
            verbose=verbose,
            intro=f"{intro}test_validate_raises_#index_{index}_",
        )
        assert_function_valid_input(
            subtests,
            check_return_bool_false,
            valid_params=(val,),
            verbose=verbose,
            intro=f"{intro}test_validate_return_bool_#index_{index}_",
        )


_DESIGN_NOTES = """
# assert_rule_validate (validate() Mode Matrix Blade)

## Purpose
Verifies `Rule.validate()` across every operational mode it supports:
default pass/raise, `return_value=True`, and `return_bool=True`. This is
the method-level counterpart to the standalone `validate()` function.

---

## 1. Execution Rationale & Toolkit Reuse

* **Delegated Assertion Blades:**
  Rather than hand-rolling `maybe_subtest` + `pytest.raises` plumbing,
  this helper wraps each mode check in a small local closure
  (`check_valid`, `check_return_bool_false`) and drives them through
  `simplibs.exception.testing`'s own `assert_function_valid_input` /
  `assert_function_raises` blades. This keeps subtest naming, verbose
  toggling, and failure reporting perfectly consistent with the rest of
  the `simplibs` testing ecosystem, and avoids duplicating logic that is
  already tested elsewhere.
* **Positive Path Coverage:**
  For every valid value, confirms both that `validate(val) is True` and
  that `validate(val, return_value=True) == val` — a rule that silently
  breaks value passthrough would otherwise go undetected by an `is_valid`
  or `is True` check alone.
* **Negative Path Coverage:**
  For every invalid value, confirms `validate(val)` raises `ValidationError`
  in standard mode, and confirms `validate(val, return_bool=True) is
  False` — verifying the exception-suppression escape hatch works
  independently of the raising path.

---

## 2. Scope Boundary

This helper deliberately does not assert on the *content* of the raised
`ValidationError` (label, problem, how_to_fix, ...) — that is the
responsibility of `assert_rule_build_exception`, since `validate()` and
`build_exception()` are guaranteed by contract to raise the same
exception construction path.
"""
