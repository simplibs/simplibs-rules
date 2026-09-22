from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class HasItem(Rule):
    """Container value must contain the given item.

    Rule:
        item in value

    Example:
        validate(value, HasItem("admin"))
    """

    __slots__ = ("item",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, item: Any) -> None:
        self.item = item

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value supports the 'in' operator and contains the required item
        return (

            # 1.1 Check that the value supports the __contains__ method
            hasattr(value, "__contains__")

            # 1.2 Check that the value contains the required item
            and self.item in value
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
        # 1.1 When value does not support membership (the 'in' operator)
        if not hasattr(value, "__contains__"):
            problem = f"Value {value!r} of type '{type(value).__name__}' does not support membership testing."
            how_to_fix = "Provide a container that supports the 'in' operator."
            exception_type = TypeError

        # 1.2 When value does not contain the required item
        else:
            problem = f"Value does not contain item {self.item!r}."
            how_to_fix = f"Provide a container that includes item {self.item!r}."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="HAS_ITEM_ERROR",
            label=value_name,
            expected=f"container with item {self.item!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# HasItem — Container Membership Validation Rule

## Purpose
The `HasItem` rule validates that a container object contains a specific
item. It is the general-container counterpart to `HasKey`: the underlying
mechanism (`__contains__` guard, then `item in value`) is identical, but
the vocabulary and exception shape differ because the two rules serve
different domains.

---

## 1. Execution Rationale & Safeguards

* **Explicit Interface Guard (`is_valid`):**
  Uses explicit `hasattr(value, "__contains__")` check to safely reject
  non-container objects without catching unrelated runtime errors —
  identical strategy to `HasKey`.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the input lacks `__contains__`.
  * A `ValueError` (`HAS_ITEM_ERROR`) when the container does not contain
    the specified item.

---

## 2. `ValueError`, Not `KeyError` (Unlike `HasKey`)

`HasKey` raises `KeyError` on failure because its domain is mappings,
where "missing key" is exactly what `KeyError` means in ordinary Python.
`HasItem` targets containers in general (list, tuple, set, dict values,
custom `Container` implementations) — "this item is not a member of the
collection" is a `ValueError` in every one of those domains, not a
`KeyError`, so the exception type follows the container's own semantics
rather than reusing `HasKey`'s mapping-specific choice.

---

## 3. Relationship to `IsSubsetOf`

`HasItem(x)` checks a single item's membership; `IsSubsetOf({x})` could
express the same check via a one-element reference set, but at the cost
of an unnecessary `set(...)` conversion and a set-shaped diagnostic
("subset of {x}") for what is conceptually a single-item lookup. `HasItem`
exists so single-item membership reads and fails as what it is, without
borrowing the heavier subset/superset machinery for a one-element case.

---

## 4. Exception Card Design

* **Type Failures:** Evaluated inputs without membership-test support
  format problem/fix strings as `TypeError`.
* **Missing Item Failures:** Evaluated containers missing the expected
  item format problem/fix strings as `ValueError` (`HAS_ITEM_ERROR`).
"""