from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import raise_param_not_string_error


class Contains(Rule):
    """String value must contain the given substring.

    Rule:
        substring in value

    Example:
        validate(value, Contains("@"))
    """

    __slots__ = ("substring",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, substring: str) -> None:

        # 1. Handle invalid input error
        if not isinstance(substring, str):
            raise_param_not_string_error("Contains", "substring", substring)

        # 2. Store the parameter
        self.substring = substring

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and presence of the substring
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that the value contains the required substring
            and self.substring in value
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
        # 1.1 When value is not a string
        if not isinstance(value, str):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not a string."
            how_to_fix = "Provide a string value."
            exception_type = TypeError

        # 1.2 When the string does not contain the required substring
        else:
            problem = f"Value {value!r} does not contain {self.substring!r}."
            how_to_fix = f"Provide a string containing {self.substring!r}."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="CONTAINS_ERROR",
            label=value_name,
            expected=f"string containing {self.substring!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# Contains — String Substring Validation Rule

## Purpose
The `Contains` rule validates that an input string contains a specified
substring using Python's native `in` operator.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Directly checks that `substring` is an instance of `str` during
  initialization, raising a `ParamError` if an invalid type is passed.
* **Runtime Type Safety (`is_valid`):**
  Evaluates `isinstance(value, str)` prior to executing `self.substring in
  value` to prevent runtime type exceptions.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the evaluated input is not a string.
  * A `ValueError` (`CONTAINS_ERROR`) when the string does not contain the
    required substring.

---

## 2. Exception Card Design

* **Type Failures:** Non-string inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Strings missing the target substring format
  problem/fix strings as `ValueError` (`CONTAINS_ERROR`).
"""
