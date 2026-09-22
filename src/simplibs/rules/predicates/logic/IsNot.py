from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsNot(Rule):
    """Value must NOT be identical to a specific object (identity check).

    Rule:
        value is not forbidden

    Example:
        validate(value, IsNot(None))
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

        # 1. Evaluate negative object identity
        return value is not self.forbidden

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
        problem = f"Value is identical to forbidden object {self.forbidden!r}."
        how_to_fix = f"Provide any object reference other than {self.forbidden!r}."
        exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_NOT_ERROR",
            label=value_name,
            expected=f"value not identical to {self.forbidden!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsNot — Negative Identity Validation Rule

## Purpose
The `IsNot` rule checks that an input value is **not** identical to a
forbidden object using Python's `is not` operator. It provides explicit
syntactic sugar over `Not(Is(...))` and delivers tailored diagnostic cards.

---

## 1. Execution Rationale

* **Direct Negated Identity:**
  Executes an O(1) memory address comparison (`id(value) != id(forbidden)`).
* **Performance & Safety:**
  The `is not` check guarantees maximum performance and absolute type
  safety without throwing `TypeError`.
* **Target Scenarios:**
  Most commonly used to guard against forbidden sentinels, singletons, or
  uninitialized state markers (e.g., `IsNot(None)`, `IsNot(MISSING)`).

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_NOT_ERROR` wrapping a `ValueError`.
* **Fix Guidance:** Explicitly directs the caller to supply any object
  reference other than `forbidden`.
"""
