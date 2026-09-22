from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class AllUnique(Rule):
    """Every item in an iterable value must be unique (no duplicates).

    Rule:
        len(set(value)) == len(value)

    Example:
        validate(value, AllUnique())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Handling for when value is not iterable
        if not hasattr(value, "__iter__"):
            return False

        # 2. Convert to a list for repeated inspection
        items = list(value)

        # 3. Evaluate item uniqueness
        # 3.1 Fast path for hashable items — O(n)
        try:
            return len(set(items)) == len(items)

        # 3.2 Fallback for unhashable items — O(n^2)
        except TypeError:
            seen: list[Any] = []
            for item in items:
                if item in seen:
                    return False
                seen.append(item)
            return True

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
        # 1.1 When value is not iterable
        if not hasattr(value, "__iter__"):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not iterable."
            how_to_fix = "Provide an iterable container (e.g., list, tuple, set)."
            exception_type = TypeError

        # 1.2 When value contains duplicates
        else:
            items = list(value)
            duplicates: list[Any] = []
            seen: list[Any] = []
            for item in items:
                if item in seen and item not in duplicates:
                    duplicates.append(item)
                else:
                    seen.append(item)

            problem = f"Value contains duplicate item(s): {duplicates!r}."
            how_to_fix = f"Remove duplicate item(s): {duplicates!r}."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="ALL_UNIQUE_ERROR",
            label=value_name,
            expected="all-unique items",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# AllUnique — Uniqueness Validation Rule for Iterables

## Purpose
The `AllUnique` rule validates that an iterable container contains no
duplicate elements.

---

## 1. Execution Rationale & Safeguards

* **Explicit Interface Guard (`is_valid`):**
  Uses explicit `hasattr(value, "__iter__")` check to safely reject
  non-iterable objects without catching unrelated runtime errors.
* **Hybrid Uniqueness Inspection:**
  * Fast-path set inspection (`O(n)`) for hashable elements (integers,
    strings, tuples).
  * Catches `TypeError` if items are unhashable (e.g., lists, dicts) and
    falls back to iterative comparison (`O(n^2)`).
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the input is not iterable.
  * A `ValueError` (`ALL_UNIQUE_ERROR`) when the input contains duplicates,
    explicitly listing all duplicate items.

---

## 2. Exception Card Design

* **Type Failures:** Evaluated inputs without `__iter__` support format
  problem/fix strings as `TypeError`.
* **Duplicate Failures:** Evaluated iterables with duplicate items format
  problem/fix strings as `ValueError` (`ALL_UNIQUE_ERROR`), listing exact
  duplicate values.
"""
