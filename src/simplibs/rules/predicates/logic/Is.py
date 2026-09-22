from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class Is(Rule):
    """Value must be identical to a specific object (identity, not equality).

    Rule:
        value is expected

    Example:
        validate(value, Is(None))
    """

    __slots__ = ("expected",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, expected: Any) -> None:
        self.expected = expected

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate object identity
        return value is self.expected

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
        problem = f"Value is not identical to {self.expected!r}."
        how_to_fix = f"Provide the exact object instance {self.expected!r}."
        exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_ERROR",
            label=value_name,
            expected=f"value identical to {self.expected!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# Is — Identity Validation Rule

## Purpose
The `Is` rule checks for strict object identity using Python's `is`
operator (`id(value) == id(expected)`). It is typically used for checking
sentinel values, singletons, or exact object references (such as `None`,
`True`, `False`).

---

## 1. Execution Rationale

* **Identity vs. Equality:**
  Unlike `Equals` (which checks `==`), `Is` tests whether two references
  point to the exact same object in memory.
* **Performance & Safety:**
  The `is` check is a direct C-API pointer comparison, guaranteeing O(1)
  performance and absolute type safety without throwing `TypeError`.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_ERROR` wrapping a `ValueError`.
* **Fix Guidance:** Explicitly instructs providing the exact object
  instance rather than an equal-value copy.
"""
