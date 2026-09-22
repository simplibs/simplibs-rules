from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsEmpty(Rule):
    """Value must be empty (falsy length via len()).

    Rule:
        len(value) == 0

    Example:
        validate(value, IsEmpty())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value supports the len() interface and its length is 0
        return (

            # 1.1 Check that the value supports the __len__ method
            hasattr(value, "__len__")

            # 1.2 Check that the object's length equals 0
            and len(value) == 0
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
        # 1.1 When value does not support len()
        if not hasattr(value, "__len__"):
            problem = f"Value {value!r} of type '{type(value).__name__}' does not support len()."
            how_to_fix = "Provide a sized container or collection (e.g., list, dict, str, set)."
            exception_type = TypeError

        # 1.2 When value is not empty (len > 0)
        else:
            problem = f"Value {value!r} has length {len(value)}, but expected length 0."
            how_to_fix = "Provide an empty container (e.g., [], {}, '', set())."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_EMPTY_ERROR",
            label=value_name,
            expected="empty container/collection",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsEmpty — Empty Container Validation Rule

## Purpose
The `IsEmpty` rule validates that a given collection or container supports
`len()` and has a length of zero.

---

## 1. Execution Rationale & Safeguards

* **Explicit Interface Guard (`is_valid`):**
  Uses explicit `hasattr(value, "__len__")` check to safely reject
  non-sized objects without catching unrelated runtime errors inside
  custom `__len__` implementations.
* **Dual Diagnostic Path (`build_exception`):**
  Uses identical internal `if/else` branching on `hasattr(value, "__len__")`
  to assemble:
  * A `TypeError` when the input lacks `__len__`.
  * A `ValueError` (`IS_EMPTY_ERROR`) when the input is a valid sized
    container with `len > 0`.

---

## 2. Exception Card Design

* **Type Failures:** Evaluated inputs without `__len__` support format
  problem/fix strings as `TypeError`.
* **Non-Empty Failures:** Evaluated containers that contain elements format
  problem/fix strings as `ValueError` (`IS_EMPTY_ERROR`), showing the
  actual length versus the expected zero length.
"""
