from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsWhitespace(Rule):
    """String value must consist entirely of whitespace characters.

    Rule:
        value.isspace()

    Example:
        validate(value, IsWhitespace())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and whitespace content
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that every character is whitespace (also rejects "")
            and value.isspace()
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

        # 1.2 When the string contains non-whitespace characters (or is empty)
        else:
            problem = f"Value {value!r} contains non-whitespace characters or is empty."
            how_to_fix = "Provide a non-empty string consisting only of whitespace characters."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_WHITESPACE_ERROR",
            label=value_name,
            expected="a non-empty, purely whitespace string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


# ----------------------------------------------------------------------
# Helper function for internal validation across the project
# ----------------------------------------------------------------------
is_whitespace = IsWhitespace().is_valid


_DESIGN_NOTES = """
# IsWhitespace — Whitespace String Validation Rule

## Purpose
The `IsWhitespace` rule validates that a string consists entirely of whitespace
characters via Python's native `str.isspace()`.

---

## 1. Execution Rationale & Safeguards

* **Empty String Rejected:**
  `"".isspace()` returns `False` in Python — this rule inherits that behavior directly.
* **Unicode Whitespace:**
  `str.isspace()` accepts spaces, tabs (`\t`), newlines (`\n`), carriage returns (`\r`),
  and all Unicode whitespace characters.

---

## 2. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at all;
  `ValueError` (`IS_WHITESPACE_ERROR`) when it is a string but fails the whitespace check.
"""