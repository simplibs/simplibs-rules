from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsAlpha(Rule):
    """String value must consist entirely of alphabetic characters.

    Rule:
        value.isalpha()

    Example:
        validate(value, IsAlpha())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and alphabetic content
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that every character is alphabetic (also rejects "")
            and value.isalpha()
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

        # 1.2 When the string contains non-alphabetic characters (or is empty)
        else:
            problem = f"Value {value!r} contains non-alphabetic characters or is empty."
            how_to_fix = "Provide a non-empty string containing only alphabetic characters."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_ALPHA_ERROR",
            label=value_name,
            expected="a non-empty, purely alphabetic string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsAlpha — Alphabetic String Validation Rule

## Purpose
The `IsAlpha` rule validates that a string consists entirely of
alphabetic characters, via Python's native `str.isalpha()`.

---

## 1. Execution Rationale & Safeguards

* **Empty String Rejected:**
  `"".isalpha()` returns `False` in Python — this rule inherits that
  behavior directly rather than special-casing it, so an empty string
  fails with the same diagnostic as one containing digits/punctuation.
  Compose explicitly with `is_blank`/`is_empty` if "empty or alphabetic"
  is ever the actual intent.
* **Unicode-Aware:**
  `str.isalpha()` follows Python's own Unicode category rules (accented
  letters count as alphabetic), not an ASCII-only `a-zA-Z` check —
  combine with `is_ascii` if only ASCII letters should pass.

---

## 2. Relationship to Sibling Rules

`IsAlpha`/`IsAlnum`/`IsDigitString`/`IsAscii`/`IsLowercase`/`IsUppercase`/
`IsTitlecase` all share the exact same shape: `isinstance(value, str) and
value.<method>()`. Kept as separate one-rule-per-file classes rather than
one generic "string method" rule, consistent with the rest of the library
(each rule independently discoverable, documented, and diagnosable) — see
`IsTitlecase.py`'s design notes for the one place this repetition is
called out and a possible future factory function is discussed.

---

## 3. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at
  all; `ValueError` (`IS_ALPHA_ERROR`) when it is a string but fails the
  character-class check (including the empty-string case).
"""
