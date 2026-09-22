from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsType(Rule):
    """Value must itself be a type (a class object, not an instance).

    Rule:
        isinstance(value, type)

    Example:
        validate(value, IsType())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is itself a class/type
        return isinstance(value, type)

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
        problem = f"Value {value!r} is an instance of '{type(value).__name__}', not a class object itself."
        how_to_fix = "Provide a class object (type), not an instance."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_TYPE_ERROR",
            label=value_name,
            expected="a class (type object)",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsType — Type/Class Object Inspection Rule

## Purpose
The `IsType` rule validates that an input value is itself a Python
class/type object (an instance of `type`), rather than an instance of a
class.

---

## 1. Execution Rationale & Safeguards

* **Direct Class Checking:**
  Evaluates `isinstance(value, type)`. Returns `True` for built-in types
  (`int`, `str`), custom classes, and metaclasses.
* **Sub-Control Delegate:**
  Serves as the central error builder when other rules (such as
  `IsSubclass`) encounter an input value that is an instance instead of a
  class type.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_TYPE_ERROR` wrapping a `TypeError`.
* **Fix Guidance:** Clear instruction requiring a class/type object
  instead of an instantiated object.
"""
