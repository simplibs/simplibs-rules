from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import raise_param_not_string_error


class StartsWith(Rule):
    """String value must start with the given prefix.

    Rule:
        value.startswith(prefix)

    Example:
        validate(value, StartsWith("https://"))
    """

    __slots__ = ("prefix",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, prefix: str) -> None:

        # 1. Handle invalid input error
        if not isinstance(prefix, str):
            raise_param_not_string_error("StartsWith", "prefix", prefix)

        # 2. Store the parameter
        self.prefix = prefix

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and the starting prefix
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that the value starts with the required prefix
            and value.startswith(self.prefix)
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

        # 1.2 When the string does not start with the required prefix
        else:
            problem = f"Value {value!r} does not start with {self.prefix!r}."
            how_to_fix = f"Provide a string starting with {self.prefix!r}."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="STARTS_WITH_ERROR",
            label=value_name,
            expected=f"string starting with {self.prefix!r}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# StartsWith — String Prefix Validation Rule

## Purpose
The `StartsWith` rule validates that an input string starts with a
specified prefix using Python's native `str.startswith()` method.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Directly checks that `prefix` is an instance of `str` during
  initialization, raising a `ParamError` if an invalid type is passed.
* **Runtime Type Safety (`is_valid`):**
  Evaluates `isinstance(value, str)` prior to calling
  `value.startswith(self.prefix)` to avoid runtime type exceptions.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the evaluated input is not a string.
  * A `ValueError` (`STARTS_WITH_ERROR`) when the string does not start
    with the required prefix.

---

## 2. Exception Card Design

* **Type Failures:** Non-string inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Strings missing the target prefix format problem/fix
  strings as `ValueError` (`STARTS_WITH_ERROR`).
"""
