import re
from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import (
    raise_param_not_string_error,
    raise_regex_param_invalid_pattern_error
)


class Regex(Rule):
    """String value must match the given regular expression pattern.

    Rule:
        re.compile(pattern).search(value) is not None

    Example:
        validate(value, Regex(r"^[a-z]+$"))
    """

    __slots__ = ("pattern", "compiled")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, pattern: str) -> None:

        # 1. Handle invalid input type error
        if not isinstance(pattern, str):
            raise_param_not_string_error("Regex", "pattern", pattern)

        # 2. Precompile the regex pattern
        try:
            self.compiled = re.compile(pattern)
        except re.error as err:
            raise_regex_param_invalid_pattern_error(pattern, err)

        # 3. Store the parameter
        self.pattern = pattern

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and search for the pattern
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that the value matches the regular expression
            and self.compiled.search(value) is not None
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
            how_to_fix = f"Provide a string matching pattern /{self.pattern}/."
            exception_type = TypeError

        # 1.2 When the string does not match the regular expression
        else:
            problem = f"Value {value!r} does not match pattern /{self.pattern}/."
            how_to_fix = f"Ensure the string format matches regex pattern /{self.pattern}/."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="REGEX_ERROR",
            label=value_name,
            expected=f"string matching pattern /{self.pattern}/",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# Regex — Regular Expression Pattern Match Rule

## Purpose
The `Regex` rule validates that an input value is a string and satisfies a
given regular expression pattern.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Directly checks that `pattern` is a `str` and uses `re.compile(pattern)`
  to precompile the regex during initialization for optimal performance.
  Raises `ParamError` for type errors or invalid regex syntax (`re.error`).
* **Runtime Type Safety (`is_valid`):**
  Evaluates `isinstance(value, str)` prior to calling
  `self.compiled.search(value)` to avoid type runtime errors.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the evaluated input is not a string.
  * A `ValueError` (`REGEX_ERROR`) when the string does not match the
    compiled regex pattern.

---

## 2. Exception Card Design

* **Type Failures:** Non-string inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Non-matching strings format problem/fix strings as
  `ValueError` (`REGEX_ERROR`), enclosing pattern in forward slashes e.g.
  `/pattern/`.
"""
