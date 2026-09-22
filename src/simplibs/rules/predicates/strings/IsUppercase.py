from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsUppercase(Rule):
    """String value must be entirely uppercase.

    Rule:
        value.isupper()

    Example:
        validate(value, IsUppercase())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and uppercase content
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that all cased characters are uppercase, and at
            #     least one cased character is present
            and value.isupper()
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

        # 1.2 When the string has no cased characters, or contains a
        #     lowercase one
        else:
            problem = f"Value {value!r} contains a lowercase character or has no cased characters."
            how_to_fix = "Provide a string that is entirely uppercase (with at least one letter)."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_UPPERCASE_ERROR",
            label=value_name,
            expected="an entirely uppercase string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsUppercase — Uppercase String Validation Rule

## Purpose
The `IsUppercase` rule validates that a string is entirely uppercase, via
Python's native `str.isupper()`. Mirror image of `IsLowercase` — see its
design notes for the shared rationale (at-least-one-cased-character
requirement, digits/punctuation being ignored rather than rejected).

---

## 1. Relationship to Sibling Rules

See `IsAlpha.py`'s design notes, section 2, and `IsLowercase.py`'s design
notes, section 2, for the shared shape/independent-implementation
rationale this rule follows.

---

## 2. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at
  all; `ValueError` (`IS_UPPERCASE_ERROR`) when it is a string but has a
  lowercase character or no cased characters at all.
"""
