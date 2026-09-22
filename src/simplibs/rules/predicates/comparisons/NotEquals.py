from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class NotEquals(Rule):
    """Value must not be equal (!=) to a specific object.

    Rule:
        value != forbidden

    Example:
        validate(value, NotEquals(0))
    """

    __slots__ = ("forbidden",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, forbidden: Any) -> None:
        self.forbidden = forbidden

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate inequality
        return value != self.forbidden

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
        problem = f"Value {value!r} is equal to forbidden value {self.forbidden!r}."
        how_to_fix = f"Provide a value other than {self.forbidden!r}."
        exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="NOT_EQUALS_ERROR",
            label=value_name,
            expected=f"value not equal to {self.forbidden!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# NotEquals — Inequality Exclusion Rule

## Purpose
The `NotEquals` rule validates that an input value is not equal (`!=`) to a
specific forbidden object or value.

---

## 1. Execution & Type Safety

* **Universal Comparison:**
  Accepts any value types. In Python, inequality checks (`!=`) safely
  return `True` for non-matching or incompatible types without throwing
  `TypeError`.
* **Zero Exception Overhead:**
  Requires no exception handling in `is_valid` as inequality checks are
  natively safe across Python types.

---

## 2. Exception Card Design

* **Error Classification:** Uses `NOT_EQUALS_ERROR` wrapping a
  `ValueError`.
* **Fix Guidance:** Provides immediate actionable advice to substitute the
  forbidden value.
"""
