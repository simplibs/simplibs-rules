from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class Equals(Rule):
    """Value must be strictly equal to the expected target.

    Rule:
        value == expected_value

    Example:
        validate(value, Equals("active"))
    """

    __slots__ = ("expected_value",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, expected_value: Any) -> None:
        self.expected_value = expected_value

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate equality
        return value == self.expected_value

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Prepare data
        problem = f"Value {value!r} is not equal to expected {self.expected_value!r}."
        how_to_fix = f"Provide a value equal to {self.expected_value!r}."
        exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="EQUALS_ERROR",
            label=value_name,
            expected=f"{self.expected_value!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# Equals — Value Equality Validation Rule

## Purpose
The `Equals` rule validates that an input value is equal (`==`) to an
expected target value.

---

## 1. Execution Rationale & Direct Equality Checks

* **Universal Safe Comparison:**
  Evaluates `value == self.expected_value`. In Python, equality comparison
  (`==`) between incompatible types safely evaluates to `False` without
  raising `TypeError`.
* **Zero Exception Overhead:**
  No exception handling is required in `is_valid` as standard equality
  checks do not raise type errors across different Python objects.

---

## 2. Exception Card Design

* **Error Classification:** Uses `EQUALS_ERROR` wrapping a `ValueError`.
* **Diagnostic Detail:** Clearly presents both the actual evaluated value
  and expected target.
"""
