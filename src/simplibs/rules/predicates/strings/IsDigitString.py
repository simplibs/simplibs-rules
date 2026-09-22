from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsDigitString(Rule):
    """String value must consist entirely of digit characters.

    Rule:
        value.isdigit()

    Example:
        validate(value, IsDigitString())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and digit content
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that every character is a digit (also rejects "")
            and value.isdigit()
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

        # 1.2 When the string contains non-digit characters (or is empty)
        else:
            problem = f"Value {value!r} contains non-digit characters or is empty."
            how_to_fix = "Provide a non-empty string containing only digit characters."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_DIGIT_STRING_ERROR",
            label=value_name,
            expected="a non-empty, purely numeric-digit string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsDigitString — Digit-Only String Validation Rule

## Purpose
The `IsDigitString` rule validates that a string consists entirely of
digit characters, via Python's native `str.isdigit()`.

---

## 1. Execution Rationale & Safeguards

* **Why Not `IsDigit`:**
  Named `IsDigitString` rather than `IsDigit`, deliberately, to avoid any
  suggestion that this validates a single character or a numeric *value*
  — it validates a *string's character class*, the same category as
  `IsAlpha`/`IsAlnum`, and stays clearly distinct from `IsInteger` (which
  validates an actual `int` value, not its string representation).
* **Empty String Rejected:** Same convention as `IsAlpha`/`IsAlnum` —
  `"".isdigit()` is `False`.
* **Not the Same As `IsInteger`:** `IsDigitString("007").is_valid("007")`
  passes (leading zeros are fine — it's a character-class check, not a
  numeric parse), whereas converting `"007"` to `int` and validating with
  `IsInteger` is a completely different, unrelated operation. Compose
  with `Compose(int, IsInteger())` (see `Compose`'s own docs) if the goal
  is "string that parses to an integer", not "string made of digit
  characters".
* **Superscript/Unicode Digits:** `str.isdigit()` also accepts some
  Unicode digit characters that are not plain ASCII `0-9` (e.g.
  superscript `²`) — combine with `is_ascii` if strict ASCII digits are
  required.

---

## 2. Relationship to Sibling Rules

See `IsAlpha.py`'s design notes, section 2 — same shared shape and
rationale for keeping these as independent, one-rule-per-file classes.

---

## 3. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at
  all; `ValueError` (`IS_DIGIT_STRING_ERROR`) when it is a string but
  fails the character-class check (including the empty-string case).
"""
