from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class NotBlank(Rule):
    """String value must contain at least one non-whitespace character.

    Rule:
        value.strip() != ""

    Example:
        validate(value, NotBlank())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and the presence of non-whitespace characters
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that the value contains at least one non-whitespace character
            and value.strip() != ""
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
            how_to_fix = "Provide a string with at least one non-whitespace character."
            exception_type = TypeError

        # 1.2 When the string is empty or contains only whitespace
        else:
            problem = f"Value {value!r} is empty or contains only whitespace."
            how_to_fix = "Provide a string with at least one non-whitespace character."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="NOT_BLANK_ERROR",
            label=value_name,
            expected="non-blank string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# NotBlank — Non-Blank String Validation Rule

## Purpose
The `NotBlank` rule validates that a string contains at least one
non-whitespace character.

---

## 1. Execution Rationale & Safeguards

* **Runtime Type Safety (`is_valid`):**
  Evaluates `isinstance(value, str)` prior to calling `value.strip() !=
  ""` to safely return `False` for non-string objects.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the evaluated input is not a string.
  * A `ValueError` (`NOT_BLANK_ERROR`) when the string is empty or
    whitespace-only.

---

## 2. Exception Card Design

* **Type Failures:** Non-string inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Empty or whitespace-only strings format problem/fix
  strings as `ValueError` (`NOT_BLANK_ERROR`).
"""
