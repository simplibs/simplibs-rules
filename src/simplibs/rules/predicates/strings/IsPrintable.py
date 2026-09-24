from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsPrintable(Rule):
    """String value must consist entirely of printable characters.

    Rule:
        value.isprintable()

    Example:
        validate(value, IsPrintable())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and printable content
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that every character is printable (accepts empty string "")
            and value.isprintable()
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

        # 1.2 When the string contains unprintable characters
        else:
            problem = f"Value {value!r} contains unprintable or control characters."
            how_to_fix = "Provide a string containing only printable characters."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_PRINTABLE_ERROR",
            label=value_name,
            expected="a printable string (no control characters)",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


# ----------------------------------------------------------------------
# Helper function for internal validation across the project
# ----------------------------------------------------------------------
is_printable = IsPrintable().is_valid


_DESIGN_NOTES = """
# IsPrintable — Printable String Validation Rule

## Purpose
The `IsPrintable` rule validates that a string consists entirely of printable
characters via Python's native `str.isprintable()`.

---

## 1. Execution Rationale & Safeguards

* **Empty String Accepted:**
  `"".isprintable()` returns `True` in Python.
* **Control Characters Rejected:**
  Characters considered non-printable (such as unescaped control codes like `\x00`)
  will cause validation to fail.

---

## 2. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at all;
  `ValueError` (`IS_PRINTABLE_ERROR`) when it is a string but contains unprintable characters.
"""