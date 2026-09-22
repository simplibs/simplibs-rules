from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsHashable(Rule):
    """Value must be hashable (usable as a dict key / set member).

    Rule:
        hash(value)

    Example:
        validate(value, IsHashable())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate hashability using the built-in hash() function
        try:
            hash(value)
            return True

        # 2. Fallback for unhashable input
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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not hashable."
        how_to_fix = (
            "Provide a hashable value (e.g. immutable types like int, str, tuple; avoid list, dict, set)."
        )
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_HASHABLE_ERROR",
            label=value_name,
            expected="hashable value",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsHashable — Hashable Object Inspection Rule

## Purpose
The `IsHashable` rule validates whether an input value is hashable and can
be used as a dictionary key or set member in Python.

---

## 1. Execution Rationale & Safeguards

* **Direct Built-in Evaluation:**
  Executes `hash(value)` directly inside a targeted `try/except TypeError`
  block. This guarantees 100% standard compliance, correctly flagging
  mutable objects (`list`, `dict`, `set`) and custom classes with
  `__hash__ = None`.
* **Safe Traversal:**
  Catches `TypeError` safely in `is_valid` without throwing uncaught
  exceptions.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_HASHABLE_ERROR` wrapping a
  `TypeError`.
* **Fix Guidance:** Advises using immutable datatypes (e.g. `tuple` instead
  of `list`).
"""
