from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import raise_param_not_string_error


class HasAttribute(Rule):
    """Value must have the given attribute.

    Rule:
        hasattr(value, attr_name)

    Example:
        validate(value, HasAttribute("append"))
    """

    __slots__ = ("attr_name",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, attr_name: str) -> None:
        # 1. Handle invalid input type error
        if not isinstance(attr_name, str):
            raise_param_not_string_error("HasAttribute", "attr_name", attr_name)

        # 2. Store the parameter
        self.attr_name = attr_name

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate attribute presence
        return hasattr(value, self.attr_name)

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
        problem = f"Object of type '{type(value).__name__}' does not have attribute {self.attr_name!r}."
        how_to_fix = f"Provide an object that supports the {self.attr_name!r} attribute or method."
        exception_type = AttributeError

        # 2. Build the exception
        return ValidationError(
            error_name="ATTRIBUTE_ERROR",
            label=value_name,
            expected=f"object with attribute {self.attr_name!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# HasAttribute — Attribute Existence Inspection Rule

## Purpose
The `HasAttribute` rule verifies duck-typing compatibility by checking
whether a target object possesses a specific attribute or method.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Directly checks that `attr_name` is an instance of `str` during
  initialization, raising a `ParamError` if an invalid type is passed.
* **Duck Typing Inspection:**
  Uses Python's built-in `hasattr()`, which safely supports both standard
  object properties and callable methods across any Python object type
  without throwing runtime type errors.

---

## 2. Exception Card Design

* **Error Classification:** Uses `ATTRIBUTE_ERROR` wrapping an
  `AttributeError`.
* **Problem Detail:** Mentions the exact runtime type
  (`type(value).__name__`) to quickly identify why the attribute was
  missing.
"""
