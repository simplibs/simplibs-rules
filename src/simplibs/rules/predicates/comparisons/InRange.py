from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import (
    raise_param_min_max_bounds_inverted_error,
    raise_param_min_max_incomparable_error
)


class InRange(Rule):
    """Value must fall within the specified numerical or ordinal range.

    Rule:
        min_val < value > max_val
        min_val <= value >= max_val

    Example:
        validate(value, InRange(1, 10))
        validate(value, InRange(0.0, 1.0, include_min=True, include_max=False))
    """

    __slots__ = ("min_val", "max_val", "include_min", "include_max")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(
        self,
        min_val: Any,
        max_val: Any,
        include_min: bool = True,
        include_max: bool = True,
    ) -> None:

        # 1. Handle inverted-order and incomparable-boundary errors
        try:
            if min_val > max_val:
                raise_param_min_max_bounds_inverted_error("InRange", min_val, max_val)
        except TypeError:
            raise_param_min_max_incomparable_error("InRange", min_val, max_val)

        # 2. Store parameters
        self.min_val = min_val
        self.max_val = max_val
        self.include_min = include_min
        self.include_max = include_max

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the comparison relation
        try:

            # 1.1 Check the lower boundary
            # 1.1.1 Check including the lower value
            if self.include_min:
                if value < self.min_val:
                    return False

            # 1.1.2 Check excluding the lower value
            else:
                if value <= self.min_val:
                    return False

            # 1.2 Check the upper boundary
            # 1.2.1 Check including the upper value
            if self.include_max:
                if value > self.max_val:
                    return False

            # 1.2.2 Check excluding the upper value
            else:
                if value >= self.max_val:
                    return False

            # 1.3 Report successful validation
            return True

        # 2. Fallback for incomparable input
        except TypeError:
            return False

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
        try:
            # Test comparability of types against both the lower and upper boundary
            _ = self.min_val <= value <= self.max_val

            # 1.1 When the types are comparable, but the value lies outside the range
            left_bracket = "[" if self.include_min else "("
            right_bracket = "]" if self.include_max else ")"
            expected_range = f"{left_bracket}{self.min_val!r}, {self.max_val!r}{right_bracket}"

            problem = f"Value {value!r} falls outside the expected range {expected_range}."
            how_to_fix = f"Provide a value within the range {expected_range}."
            exception_type = ValueError

        except TypeError:
            # 1.2 When the value's type cannot be compared with the range boundaries
            problem = (
                f"Cannot compare '{type(value).__name__}' ({value!r}) with range bounds "
                f"'{type(self.min_val).__name__}' ({self.min_val!r}) and '{type(self.max_val).__name__}' ({self.max_val!r})."
            )
            how_to_fix = f"Provide a value of a type comparable with '{type(self.min_val).__name__}'."
            exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IN_RANGE_ERROR",
            label=value_name,
            expected=f"value in range {self.min_val!r} to {self.max_val!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# InRange — Range Bounds Comparison Validation Rule

## Purpose
The `InRange` rule validates that an input value falls within specified
lower (`min_val`) and upper (`max_val`) bounds, supporting configurable
inclusivity via `include_min` and `include_max`.

---

## 1. Execution Rationale & Boundary Validation

* **Constructor Fail-Fast:**
  Directly checks that `min_val <= max_val` during instantiation, raising a
  `ParamError` if boundaries are inverted or mutually incompatible.
* **Safe Evaluation (`is_valid`):**
  Uses targeted `try/except TypeError` around boundary comparisons to
  safely return `False` when comparing incompatible types.
* **Dual Diagnostic Path (`build_exception`):**
  Directly tests boundary comparisons to differentiate:
  * A `TypeError` when the input type cannot be compared with the boundary
    types.
  * A `ValueError` (`IN_RANGE_ERROR`) when the value is comparable but
    falls outside the inclusive/exclusive mathematical bounds.

---

## 2. Exception Card Design

* **Type Failures:** Incompatible type comparisons format problem/fix
  strings as `TypeError`.
* **Value Failures:** Out-of-bounds inputs format problem/fix strings as
  `ValueError` (`IN_RANGE_ERROR`), clearly indicating boundary mathematical
  notation e.g., `[min, max]`.
"""
