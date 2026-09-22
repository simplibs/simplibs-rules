from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import raise_param_not_string_error


class EndsWith(Rule):
    """String value must end with the given suffix.

    Rule:
        value.endswith(suffix)

    Example:
        validate(value, EndsWith(".py"))
    """

    __slots__ = ("suffix",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, suffix: str) -> None:

        # 1. Handle invalid input error
        if not isinstance(suffix, str):
            raise_param_not_string_error("EndsWith", "suffix", suffix)

        # 2. Store the parameter
        self.suffix = suffix

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and the ending suffix
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that the value ends with the required suffix
            and value.endswith(self.suffix)
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

        # 1.2 When the string does not end with the required suffix
        else:
            problem = f"Value {value!r} does not end with {self.suffix!r}."
            how_to_fix = f"Provide a string ending with {self.suffix!r}."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="ENDS_WITH_ERROR",
            label=value_name,
            expected=f"string ending with {self.suffix!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# EndsWith — String Suffix Validation Rule

## Purpose
The `EndsWith` rule validates that an input string ends with a specified
suffix using Python's native `str.endswith()` method.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Directly checks that `suffix` is an instance of `str` during
  initialization, raising a `ParamError` if an invalid type is passed.
* **Runtime Type Safety (`is_valid`):**
  Evaluates `isinstance(value, str)` prior to calling
  `value.endswith(self.suffix)` to avoid `AttributeError` or `TypeError`.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the evaluated input is not a string.
  * A `ValueError` (`ENDS_WITH_ERROR`) when the string does not end with
    the required suffix.

---

## 2. Exception Card Design

* **Type Failures:** Non-string inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Strings missing the target suffix format problem/fix
  strings as `ValueError` (`ENDS_WITH_ERROR`).
"""
