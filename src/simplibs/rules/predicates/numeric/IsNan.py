from typing import Any
import math
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsNan(Rule):
    """Value must be a float NaN.

    Rule:
        math.isnan(value)

    Example:
        validate(value, IsNan())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the float type and the NaN value
        return (

            # 1.1 Check that the value is of type float
            isinstance(value, float)

            # 1.2 Check that the value represents NaN
            and math.isnan(value)
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
        # 1.1 When it's not a float
        if not isinstance(value, float):
            problem = f"Value {value!r} is of type '{type(value).__name__}', expected float."
            how_to_fix = "Provide float('nan')."
            exception_type = TypeError
            expected = "float('nan')"
        else:
            # 1.2 When it's a float, but not NaN
            problem = f"Value {value!r} is a regular (non-NaN) float."
            how_to_fix = "Provide float('nan')."
            exception_type = ValueError
            expected = "float('nan')"

        # 2. Build the exception
        return ValidationError(
            error_name="IS_NAN_ERROR",
            label=value_name,
            expected=expected,
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsNan — Float NaN Validation Rule

## Purpose
The `IsNan` rule validates that an input value is a float representing
Not-a-Number (`float('nan')`).

---

## 1. Execution Rationale & Safeguards

* **Two-Stage Check:**
  Requires `isinstance(value, float)` and `math.isnan(value)`.
* **Dual Diagnostic Path (`build_exception`):**
  * `TypeError` when the evaluated input is not a `float`.
  * `ValueError` (`IS_NAN_ERROR`) when the float input is a regular
    non-NaN float.

---

## 2. Exception Card Design

* **Type Failures:** Non-float inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Regular float inputs format problem/fix strings as
  `ValueError` (`IS_NAN_ERROR`).
"""
