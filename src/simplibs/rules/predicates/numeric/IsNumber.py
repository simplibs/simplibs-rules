from typing import Any
from decimal import Decimal
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsNumber(Rule):
    """Value must be a number (int, float, complex, Decimal — booleans excluded).

    Rule:
        isinstance(value, (int, float, Decimal, complex)) and not isinstance(value, bool)

    Example:
        validate(value, IsNumber())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether this is a numeric type (excluding bool)
        return (
            isinstance(value, (int, float, Decimal, complex))
            and not isinstance(value, bool)
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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not a numeric value."
        how_to_fix = "Provide a numeric value (int, float, Decimal, complex; booleans excluded)."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_NUMBER_ERROR",
            label=value_name,
            expected="a number",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


# ----------------------------------------------------------------------
# Helper function for internal validation across the project
# ----------------------------------------------------------------------
is_number = IsNumber().is_valid


_DESIGN_NOTES = """
# IsNumber — General Numeric Type Validation Rule

## Purpose
The `IsNumber` rule validates that an input value belongs to Python's
numeric types (excluding booleans).

---

## 1. Execution Rationale & Safeguards

* **Broad Numeric Type Support:**
  Validates against standard Python numeric representations (`int`,
  `float`, `Decimal`, `complex`), ensuring booleans are safely filtered
  out.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_NUMBER_ERROR` wrapping a `TypeError`.

---

## 3. Ecosystem Integration

* **Internal `is_number` Helper:**
  Exposes `is_number = IsNumber().is_valid` at module level, following the
  same pattern as `is_integer` and `is_primitive_number`. `IsZero`
  imports this to distinguish non-numeric input (`TypeError`) from a
  numeric-but-nonzero value (`ValueError`) in `build_exception`.
"""
