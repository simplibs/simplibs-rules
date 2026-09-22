from typing import Any
import math
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsInfinity(Rule):
    """Value must be positive or negative infinity.

    Rule:
        math.isinf(value)

    Example:
        validate(value, IsInfinity())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the float type and infinity
        return (

            # 1.1 Check that the value is of type float
            isinstance(value, float)

            # 1.2 Check that the value represents infinity
            and math.isinf(value)
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
        # 1.1 If it's not a float
        if not isinstance(value, float):
            problem = f"Value {value!r} is of type '{type(value).__name__}', expected float."
            how_to_fix = "Provide a float representing infinity, e.g. float('inf') or float('-inf')."
            exception_type = TypeError
            expected = "float('inf') or float('-inf')"
        else:
            # 1.2 If it's a float, but finite (or NaN)
            problem = f"Value {value!r} is a finite float."
            how_to_fix = "Provide float('inf') or float('-inf')."
            exception_type = ValueError
            expected = "float('inf') or float('-inf')"

        # 2. Build the exception
        return ValidationError(
            error_name="IS_INFINITY_ERROR",
            label=value_name,
            expected=expected,
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsInfinity — Infinity Float Validation Rule

## Purpose
The `IsInfinity` rule validates that an input value is a float
representing positive or negative infinity.

---

## 1. Execution Rationale & Safeguards

* **Type and Boundary Checks:**
  Requires `isinstance(value, float)` followed by `math.isinf(value)`.
* **Dual Diagnostic Path (`build_exception`):**
  * `TypeError` when the evaluated input is not a `float`.
  * `ValueError` (`IS_INFINITY_ERROR`) when the float input is finite.

---

## 2. Exception Card Design

* **Type Failures:** Non-float inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Finite float inputs format problem/fix strings as
  `ValueError` (`IS_INFINITY_ERROR`).
"""
