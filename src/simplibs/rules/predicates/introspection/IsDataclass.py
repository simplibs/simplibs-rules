from typing import Any
import dataclasses
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsDataclass(Rule):
    """Value must be a dataclass (instance or the class itself).

    Rule:
        dataclasses.is_dataclass(value)

    Example:
        validate(value, IsDataclass())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether this is a dataclass (instance or class)
        return dataclasses.is_dataclass(value)

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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not a dataclass."
        how_to_fix = "Provide an instance of, or a class decorated with, @dataclass."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_DATACLASS_ERROR",
            label=value_name,
            expected="dataclass instance or type",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsDataclass — Dataclass Inspection Rule

## Purpose
The `IsDataclass` rule validates that an input value is either an instance
of a dataclass or a class decorated with `@dataclass`.

---

## 1. Execution Rationale & Safeguards

* **Standard Library Inspection:**
  Relies directly on `dataclasses.is_dataclass(value)`.
* **Universal Acceptance:**
  Returns `True` for both instance objects and class types created via
  `@dataclass`.
* **Zero Exception Overhead:**
  The `is_dataclass` check safely handles arbitrary input types (integers,
  strings, functions, None) without raising runtime exceptions.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_DATACLASS_ERROR` wrapping a
  `TypeError`.
* **Fix Guidance:** Explicit advice to provide a `@dataclass`-decorated
  class or instance.
"""
