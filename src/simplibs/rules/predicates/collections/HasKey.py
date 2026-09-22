from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class HasKey(Rule):
    """Mapping value must contain the given key.

    Rule:
        key in value

    Example:
        validate(value, HasKey("id"))
    """

    __slots__ = ("key",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, key: Any) -> None:
        self.key = key

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value supports the 'in' operator and contains the required key
        return (

            # 1.1 Check that the value supports the __contains__ method
            hasattr(value, "__contains__")

            # 1.2 Check that the value contains the required key
            and self.key in value
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
            problem = f"Value {value!r} of type '{type(value).__name__}' does not support key lookup."
            how_to_fix = "Provide a mapping or container that supports the 'in' operator."
            exception_type = TypeError

        # 1.2 When value does not contain the required key
        else:
            problem = f"Value does not have key {self.key!r}."
            how_to_fix = f"Provide a mapping containing key {self.key!r}."
            exception_type = KeyError

        # 2. Build the exception
        return ValidationError(
            error_name="HAS_KEY_ERROR",
            label=value_name,
            expected=f"mapping with key {self.key!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# HasKey — Mapping Key Existence Validation Rule

## Purpose
The `HasKey` rule validates that a mapping or container object contains a
specific key.

---

## 1. Execution Rationale & Safeguards

* **Explicit Interface Guard (`is_valid`):**
  Uses explicit `hasattr(value, "__contains__")` check to safely reject
  non-container objects without catching unrelated runtime errors.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the input lacks `__contains__`.
  * A `KeyError` (`HAS_KEY_ERROR`) when the target container does not
    contain the specified key.

---

## 2. Exception Card Design

* **Type Failures:** Evaluated inputs without container lookup support
  format problem/fix strings as `TypeError`.
* **Missing Key Failures:** Evaluated containers missing the expected key
  format problem/fix strings as `KeyError` (`HAS_KEY_ERROR`).
"""
