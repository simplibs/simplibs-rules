from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsPrimitiveNumber(Rule):
    """Value must be a primitive numeric type (int or float — booleans excluded).

    Rule:
        isinstance(value, (int, float)) and not isinstance(value, bool)

    Example:
        validate(value, IsPrimitiveNumber())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether this is int or float (excluding bool)
        return (
            isinstance(value, (int, float))
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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not a primitive number (int, float)."
        how_to_fix = "Provide a primitive numeric value (int or float; booleans excluded)."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_PRIMITIVE_NUMBER_ERROR",
            label=value_name,
            expected="a primitive number (int or float)",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


# ----------------------------------------------------------------------
# Helper function for internal validation across the project
# ----------------------------------------------------------------------
is_primitive_number = IsPrimitiveNumber().is_valid


_DESIGN_NOTES = """
# IsPrimitiveNumber — Primitive Numeric Type Validation Rule

## Purpose
The `IsPrimitiveNumber` rule validates that an input value belongs
specifically to Python's primitive numeric types (`int` and `float`,
excluding booleans).

---

## 1. Execution Rationale & Safeguards

* **Fast-Path Check:**
  Directly checks `isinstance(value, (int, float))` while explicitly
  excluding `bool`. Serves as an internal fast-path helper for
  mathematical rules like `CloseTo`.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_PRIMITIVE_NUMBER_ERROR` wrapping a
  `TypeError`.
"""
