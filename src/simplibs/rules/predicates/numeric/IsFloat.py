from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsFloat(Rule):
    """Value must be a float.

    Rule:
        isinstance(value, float)

    Example:
        validate(value, IsFloat())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is strictly a float
        return isinstance(value, float)

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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not a float."
        how_to_fix = "Provide a float value (e.g. 10.5)."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_FLOAT_ERROR",
            label=value_name,
            expected="a float",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsFloat — Float Type Validation Rule

## Purpose
The `IsFloat` rule validates that an input value is strictly a float
instance.

---

## 1. Execution Rationale & Safeguards

* **Strict Type Check:**
  Uses `isinstance(value, float)`. Integers and strings are rejected.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_FLOAT_ERROR` wrapping a `TypeError`.
* **Fix Guidance:** Advises providing a float value.
"""
