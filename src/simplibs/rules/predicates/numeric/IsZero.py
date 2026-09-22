from typing import Any
from decimal import Decimal
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
# Inners
from .IsNumber import is_number


class IsZero(Rule):
    """Numeric value must equal zero.

    Rule:
        value == 0

    Example:
        validate(value, IsZero())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the numeric type and the value 0
        return (

            # 1.1 Check that the value is numeric (excluding bool)
            isinstance(value, (int, float, Decimal, complex))
            and not isinstance(value, bool)

            # 1.2 Check that the value equals 0
            and value == 0
        )

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
        # 1.1 When it's not a numeric type
        if not is_number(value):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not a numeric value."
            how_to_fix = "Provide a numeric value equal to 0 (int, float, Decimal, or complex)."
            exception_type = TypeError
            expected = "numeric zero"
        else:
            # 1.2 When it's a number, but it's not 0
            problem = f"Value {value!r} is not zero."
            how_to_fix = "Provide a numeric value equal to 0."
            exception_type = ValueError
            expected = "zero"

        # 2. Build the exception
        return ValidationError(
            error_name="IS_ZERO_ERROR",
            label=value_name,
            expected=expected,
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsZero — Numeric Zero Validation Rule

## Purpose
The `IsZero` rule validates that a numeric value is equal to zero
(`value == 0`).

---

## 1. Execution Rationale & Safeguards

* **Safe Comparison:**
  Ensures input is a valid number via `is_number(value)` before performing
  the `value == 0` check in `build_exception`.
* **Dual Diagnostic Path (`build_exception`):**
  * `TypeError` when the evaluated input is not a number.
  * `ValueError` (`IS_ZERO_ERROR`) when the numeric input is non-zero.

---

## 2. Exception Card Design

* **Type Failures:** Non-numeric inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Non-zero numbers format problem/fix strings as
  `ValueError` (`IS_ZERO_ERROR`).

## Notes
* `build_exception` previously called an undefined `_is_number(value)`
  helper — no such name existed anywhere in the file or its imports, so
  reaching this branch at runtime would have raised `NameError` instead of
  the intended diagnostic. Fixed by importing the module-level `is_number`
  helper from `IsNumber` (the same helper `CloseTo`-style rules use
  elsewhere) and calling that instead.
"""
