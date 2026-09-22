from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class LessOrEqual(Rule):
    """Value must be less than or equal to the given threshold.

    Rule:
        value <= threshold

    Example:
        validate(value, LessOrEqual(100))
    """

    __slots__ = ("threshold",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, threshold: Any) -> None:
        self.threshold = threshold

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the comparison relation
        try:
            return value <= self.threshold

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
            # Test whether the types are comparable
            _ = value <= self.threshold

            # 1.1 When the types are comparable, but the value doesn't satisfy the relation
            problem = f"Value {value!r} is greater than {self.threshold!r}."
            how_to_fix = f"Provide a value less than or equal to {self.threshold!r}."
            exception_type = ValueError

        except TypeError:
            # 1.2 When the types cannot be compared with each other
            problem = f"Cannot compare '{type(value).__name__}' ({value!r}) with '{type(self.threshold).__name__}' ({self.threshold!r})."
            how_to_fix = f"Provide a value of a type comparable with '{type(self.threshold).__name__}'."
            exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="LESS_OR_EQUAL_ERROR",
            label=value_name,
            expected=f"value less than or equal to {self.threshold!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# LessOrEqual — Threshold Comparison Rule (Inclusive Maximum)

## Purpose
The `LessOrEqual` rule validates that an input value is numerically or
order-wise less than or equal to (`<=`) a given threshold.

---

## 1. Execution & Exception Safeguards

* **Safe Evaluation (`is_valid`):**
  Uses targeted `try/except TypeError` around `value <= self.threshold` to
  safely return `False` when comparing incompatible types.
* **Dual Diagnostic Path (`build_exception`):**
  Directly tests boundary comparison to differentiate:
  * A `TypeError` when types are not mutually comparable (e.g. comparing
    string to integer).
  * A `ValueError` (`LESS_OR_EQUAL_ERROR`) when the value is comparable
    but greater than the threshold.

---

## 2. Exception Card Design

* **Type Failures:** Incompatible type comparisons format problem/fix
  strings as `TypeError`.
* **Value Failures:** Out-of-bounds inputs format problem/fix strings as
  `ValueError` (`LESS_OR_EQUAL_ERROR`).
"""
