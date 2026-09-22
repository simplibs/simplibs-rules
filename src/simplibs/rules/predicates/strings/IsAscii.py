from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsAscii(Rule):
    """String value must contain only ASCII characters.

    Rule:
        value.isascii()

    Example:
        validate(value, IsAscii())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and ASCII content
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that every character is within the ASCII range
            and value.isascii()
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

        # 1.2 When the string contains non-ASCII characters
        else:
            problem = f"Value {value!r} contains non-ASCII characters."
            how_to_fix = "Provide a string containing only ASCII characters (U+0000-U+007F)."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_ASCII_ERROR",
            label=value_name,
            expected="a purely ASCII string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsAscii — ASCII-Only String Validation Rule

## Purpose
The `IsAscii` rule validates that a string contains only ASCII
characters, via Python's native `str.isascii()`.

---

## 1. Execution Rationale & Safeguards

* **The One Sibling That Accepts The Empty String:**
  Unlike `IsAlpha`/`IsAlnum`/`IsDigitString`, `"".isascii()` returns
  `True` in Python — there is no "empty string has no characters to
  classify" penalty here the way there is for a character-*class* check,
  because "contains only ASCII characters" is vacuously true for zero
  characters. This is a genuine, deliberate difference from its
  siblings, not an oversight — flagged here explicitly since every other
  rule in this batch rejects `""`.
* **Complements, Doesn't Replace, Character-Class Rules:**
  `IsAscii` says nothing about *what kind* of ASCII characters are
  present (letters vs. punctuation vs. control characters) — it is
  meant to be combined (`is_alpha & is_ascii`, `is_alnum & is_ascii`),
  not used alone when a stricter guarantee is needed.

---

## 2. Relationship to Sibling Rules

See `IsAlpha.py`'s design notes, section 2 — same shared shape and
rationale for keeping these as independent, one-rule-per-file classes.

---

## 3. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at
  all; `ValueError` (`IS_ASCII_ERROR`) when it is a string but contains
  at least one non-ASCII character.
"""
