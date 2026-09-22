from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsBlank(Rule):
    """String value must be empty or whitespace-only.

    Rule:
        value.strip() == ""

    Example:
        validate(value, IsBlank())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and emptiness (or whitespace-only)
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that the value contains only whitespace or is empty
            and value.strip() == ""
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
            how_to_fix = "Provide an empty string or a string containing only whitespace."
            exception_type = TypeError

        # 1.2 When the string contains visible non-whitespace characters
        else:
            problem = f"Value {value!r} contains non-whitespace characters."
            how_to_fix = "Provide an empty string or a string containing only whitespace."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_BLANK_ERROR",
            label=value_name,
            expected="empty or whitespace-only string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsBlank — Blank String Validation Rule

## Purpose
The `IsBlank` rule validates that a string value is either completely
empty or consists entirely of whitespace characters.

---

## 1. Execution Rationale & Safeguards

* **Runtime Type Safety (`is_valid`):**
  Evaluates `isinstance(value, str)` prior to calling `value.strip() ==
  ""` to safely return `False` for non-string objects.
* **Dual Diagnostic Path (`build_exception`):**
  Uses internal `if/else` branching to assemble:
  * A `TypeError` when the evaluated input is not a string.
  * A `ValueError` (`IS_BLANK_ERROR`) when the string contains
    non-whitespace characters.

---

## 2. Exception Card Design

* **Type Failures:** Non-string inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Strings with content format problem/fix strings as
  `ValueError` (`IS_BLANK_ERROR`).
"""
