from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsAlnum(Rule):
    """String value must consist entirely of alphanumeric characters.

    Rule:
        value.isalnum()

    Example:
        validate(value, IsAlnum())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and alphanumeric content
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that every character is alphanumeric (also rejects "")
            and value.isalnum()
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

        # 1.2 When the string contains non-alphanumeric characters (or is empty)
        else:
            problem = f"Value {value!r} contains non-alphanumeric characters or is empty."
            how_to_fix = "Provide a non-empty string containing only letters and digits."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_ALNUM_ERROR",
            label=value_name,
            expected="a non-empty, purely alphanumeric string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsAlnum — Alphanumeric String Validation Rule

## Purpose
The `IsAlnum` rule validates that a string consists entirely of
alphanumeric characters (letters and digits), via Python's native
`str.isalnum()`.

---

## 1. Execution Rationale & Safeguards

* **Empty String Rejected:** Same convention as `IsAlpha` —
  `"".isalnum()` is `False`, and this rule does not special-case it.
* **Unicode-Aware:** `str.isalnum()` follows Python's own Unicode
  category rules for both the letter and digit portions — combine with
  `is_ascii` if only ASCII letters/digits should pass.
* **Broader Than "Letters + `0-9`":** `str.isalnum()` also accepts
  Unicode numeric characters that are not plain digits in the
  `str.isdigit()` sense (e.g. superscripts) — a caller wanting a strict
  ASCII alphanumeric identifier should prefer a `regex`-based
  `validated_type` (see `simplibs.type.str_identifier`) instead.

---

## 2. Relationship to Sibling Rules

See `IsAlpha.py`'s design notes, section 2 — same shared shape and
rationale for keeping these as independent, one-rule-per-file classes.

---

## 3. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at
  all; `ValueError` (`IS_ALNUM_ERROR`) when it is a string but fails the
  character-class check (including the empty-string case).
"""
