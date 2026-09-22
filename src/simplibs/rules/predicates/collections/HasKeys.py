from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import raise_param_missing_error


class HasKeys(Rule):
    """Mapping value must contain all of the given keys.

    Rule:
        all(key in value for key in keys)

    Example:
        validate(value, HasKeys("id", "name"))
    """

    __slots__ = ("keys",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *keys: Any) -> None:

        # 1. Parameter validation (must contain at least one key)
        if not keys:
            raise_param_missing_error("HasKeys", "keys")

        # 2. Store parameters
        self.keys = keys

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value supports the 'in' operator and contains all required keys
        return (

            # 1.1 Check that the value supports the __contains__ method
            hasattr(value, "__contains__")

            # 1.2 Check that the value contains all keys
            and all(key in value for key in self.keys)
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

        # 1.2 When value does not contain all required keys
        else:
            missing = [key for key in self.keys if key not in value]
            problem = f"Value is missing key(s): {missing!r}."
            how_to_fix = f"Provide a mapping containing key(s): {missing!r}."
            exception_type = KeyError

        # 2. Build the exception
        return ValidationError(
            error_name="HAS_KEYS_ERROR",
            label=value_name,
            expected=f"mapping with keys {self.keys!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# HasKeys — Multiple Mapping Keys Validation Rule

## Purpose
The `HasKeys` rule validates that a mapping or container contains all
specified keys.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Raises a `ParamError` directly if instantiated without keys (`HasKeys()`),
  via `raise_param_missing_error("HasKeys", "keys")`.
* **Explicit Interface Guard (`is_valid`):**
  Uses explicit `hasattr(value, "__contains__")` check to safely reject
  non-container objects without catching unrelated runtime errors.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the input lacks `__contains__`.
  * A `KeyError` (`HAS_KEYS_ERROR`) when the target container is missing
    required keys, dynamically listing all missing keys.

---

## 2. Exception Card Design

* **Type Failures:** Evaluated inputs without container lookup support
  format problem/fix strings as `TypeError`.
* **Missing Keys Diagnostic:** Dynamically computes and presents missing
  keys in both `problem` and `how_to_fix` as `KeyError` (`HAS_KEYS_ERROR`).
"""
