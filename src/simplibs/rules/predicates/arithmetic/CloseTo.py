import math
from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from ..numeric.IsPrimitiveNumber import is_primitive_number
from .._init_validators import validate_param_is_primitive_number


class CloseTo(Rule):
    """Numeric value must be close to target within relative/absolute tolerance.

    Rule:
        math.isclose(value, target, rel_tol, abs_tol)

    Example:
        validate(value, CloseTo(math.pi, rel_tol=0.001))
    """

    __slots__ = ("target", "rel_tol", "abs_tol")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(
        self,
        target: float | int,
        *,
        rel_tol: float = 1e-9,
        abs_tol: float = 0.0,
    ) -> None:

        # 1. Parameter validation
        if not (
            is_primitive_number(target)
            and is_primitive_number(rel_tol)
            and is_primitive_number(abs_tol)
        ):
            validate_param_is_primitive_number("CloseTo", "target", target)
            validate_param_is_primitive_number("CloseTo", "rel_tol", rel_tol)
            validate_param_is_primitive_number("CloseTo", "abs_tol", abs_tol)

        # 2. Parameter assignment
        self.target = float(target)
        self.rel_tol = float(rel_tol)
        self.abs_tol = float(abs_tol)

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is numeric and falls within the allowed tolerance
        return (

            # 1.1 Check that the value is numeric (excluding bool)
            isinstance(value, (int, float))
            and not isinstance(value, bool)

            # 1.2 Check that the value falls within the allowed tolerance
            and math.isclose(
                value,
                self.target,
                rel_tol=self.rel_tol,
                abs_tol=self.abs_tol,
            )
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
        # 1.1 When value is not a number
        if not is_primitive_number(value):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not a primitive number."
            how_to_fix = "Provide a primitive numeric value (int or float)."
            exception_type = TypeError

        # 1.2 When value is out of tolerance
        else:
            tolerance = (
                f"rel={self.rel_tol}, abs={self.abs_tol}"
                if self.abs_tol > 0.0
                else f"rel={self.rel_tol}"
            )
            problem = f"Value {value!r} is not close to {self.target!r} (tolerance: {tolerance})."
            how_to_fix = f"Provide a value approximately equal to {self.target!r}."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="CLOSE_TO_ERROR",
            label=value_name,
            expected=f"value close to {self.target!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# CloseTo — Floating-Point Tolerance Equality Validation Rule

## Purpose
The `CloseTo` rule validates that a numeric input value is approximately
equal to a target float/int using Python's standard `math.isclose()`.

---

## 1. Execution Rationale & Fail-Fast Safeguards

* **Constructor Parameter Guard:**
  `__init__` performs a fast joint check via `is_primitive_number` on
  `target`, `rel_tol`, and `abs_tol`. On failure, it delegates sequentially
  to `validate_param_is_primitive_number` to raise a targeted `ParamError`
  specifying the exact invalid parameter.
* **Non-Numeric Value Handling:**
  In `is_valid`, non-primitive numeric inputs fail immediately (`return
  False`) using `is_primitive_number`. In `build_exception`, non-numeric
  values assemble a `TypeError` directly using internal branching.

---

## 2. Parameter Naming Strategy

* **Standard Library Alignment:**
  Uses `rel_tol` and `abs_tol` directly to mirror Python's `math.isclose()`
  API. This minimizes mapping overhead during rule evaluation and maintains
  an intuitive interface for developers.

---

## 3. Exception Card Design

* **Type Failures:** Evaluated non-numeric inputs format problem/fix
  strings as `TypeError`.
* **Tolerance Failures:** Evaluated inputs that fail proximity checks
  format problem/fix strings as `ValueError` (`CLOSE_TO_ERROR`) with exact
  tolerance settings (`rel_tol`, `abs_tol`).
"""
