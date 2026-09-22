from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import raise_param_not_string_error


class IsSubstringOf(Rule):
    """String value must be a substring of the target string.

    Rule:
        value in target_string

    Example:
        validate(value, IsSubstringOf("ADMIN_ROLE_FULL_ACCESS"))
    """

    __slots__ = ("target_string",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, target_string: str) -> None:

        # 1. Handle invalid input error
        if not isinstance(target_string, str):
            raise_param_not_string_error("IsSubstringOf", "target_string", target_string)

        # 2. Store the parameter
        self.target_string = target_string

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and whether value is a substring of target_string
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that the value is a substring of target_string
            and value in self.target_string
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

        # 1.2 When the string is not a substring of target_string
        else:
            problem = f"Value {value!r} is not a substring of {self.target_string!r}."
            how_to_fix = f"Provide a string that is contained within {self.target_string!r}."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_SUBSTRING_OF_ERROR",
            label=value_name,
            expected=f"substring of {self.target_string!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsSubstringOf — Inverse Substring Validation Rule

## Purpose
The `IsSubstringOf` rule validates that an input string is a substring of a
given target master string using Python's native `in` operator (`value in target_string`).

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Directly checks that `target_string` is an instance of `str` during
  initialization, raising a `ParamError` if an invalid type is passed.
* **Runtime Type Safety (`is_valid`):**
  Evaluates `isinstance(value, str)` prior to executing `value in self.target_string`
  to prevent runtime type exceptions.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the evaluated input is not a string.
  * A `ValueError` (`IS_SUBSTRING_OF_ERROR`) when the string is not contained
    within the target string.

---

## 2. Exception Card Design

* **Type Failures:** Non-string inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Strings that are not substrings format problem/fix
  strings as `ValueError` (`IS_SUBSTRING_OF_ERROR`).
"""