from typing import Any, Collection
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from ..collections.IsContainer import is_container
from .._init_validators import raise_param_not_container_error
from .._helpers import format_container


class IsSupersetOf(Rule):
    """Value (as a set) must be a superset of the given reference collection.

    Rule:
        set(value) >= reference

    Example:
        validate(value, IsSupersetOf({"read"}))
    """

    __slots__ = ("reference",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, reference: Collection[Any]) -> None:

        # 1. Parameter validation (must be a valid container)
        if not is_container(reference):
            raise_param_not_container_error("IsSupersetOf", "reference", reference)

        # 2. Store a precomputed set for O(1) lookups
        self.reference = set(reference)

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Handling for when value is not iterable
        if not hasattr(value, "__iter__"):
            return False

        # 2. Evaluate whether the input is a superset of the reference collection
        try:
            return set(value) >= self.reference

        # 3. Fallback for unhashable items
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

        # Deterministic representation for stable logs and tests
        ref_str = format_container(self.reference)

        # 1. Prepare data
        # 1.1 When value is not iterable
        if not hasattr(value, "__iter__"):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not iterable."
            how_to_fix = "Provide an iterable container (e.g., list, tuple, set)."
            exception_type = TypeError

        # 1.2 When value is missing required elements (or contains unhashable elements)
        else:
            try:
                missing = self.reference - set(value)
                missing_str = format_container(missing)
                problem = f"Value is missing required element(s): {missing_str}."
                how_to_fix = f"Include element(s): {missing_str}."
            except TypeError:
                problem = f"Value {value!r} contains unhashable elements that cannot be compared as a set."
                how_to_fix = "Ensure all elements in the container are hashable (e.g., strings, numbers, tuples)."

            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_SUPERSET_OF_ERROR",
            label=value_name,
            expected=f"superset of {ref_str}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsSupersetOf — Superset Relationship Validation Rule

## Purpose
The `IsSupersetOf` rule validates that an input iterable contains at least
all elements of a reference collection (i.e., input is a superset of
reference).

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Raises a `ParamError` directly if `reference` is not a standard container
  type (list, tuple, set, frozenset).
* **Precomputed Set (O(1) Lookup):**
  Converts the reference collection into a `set` during initialization.
* **Deterministic Set Representation:**
  Uses a helper `format_container` function during exception building to sort set
  elements before string formatting. This eliminates non-deterministic hash
  ordering in Python's native `set.__repr__`, guaranteeing stable exception
  messages for assertions, unit testing, and logging aggregation.
* **Explicit Interface Guard (`is_valid`):**
  Uses explicit `hasattr(value, "__iter__")` check to safely reject
  non-iterable objects. Catches `TypeError` only for unhashable elements.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the input is not iterable.
  * A `ValueError` (`IS_SUPERSET_OF_ERROR`) when the input is missing
    required items, explicitly displaying missing elements
    (`self.reference - set(value)`).

---

## 2. Exception Card Design

* **Type Failures:** Evaluated inputs without `__iter__` support format
  problem/fix strings as `TypeError`.
* **Superset Failures:** Evaluated iterables missing required items format
  problem/fix strings as `ValueError` (`IS_SUPERSET_OF_ERROR`), showing
  exact missing elements in deterministic sorted order.
"""