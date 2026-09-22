from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsLowercase(Rule):
    """String value must be entirely lowercase.

    Rule:
        value.islower()

    Example:
        validate(value, IsLowercase())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and lowercase content
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that all cased characters are lowercase, and at
            #     least one cased character is present
            and value.islower()
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

        # 1.2 When the string has no cased characters, or contains an
        #     uppercase one
        else:
            problem = f"Value {value!r} contains an uppercase character or has no cased characters."
            how_to_fix = "Provide a string that is entirely lowercase (with at least one letter)."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_LOWERCASE_ERROR",
            label=value_name,
            expected="an entirely lowercase string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsLowercase — Lowercase String Validation Rule

## Purpose
The `IsLowercase` rule validates that a string is entirely lowercase, via
Python's native `str.islower()`.

---

## 1. Execution Rationale & Safeguards

* **Requires At Least One Cased Character:**
  `str.islower()` returns `False` for a string with no cased characters
  at all (`"123".islower()` is `False`, and so is `""`.islower()`) — this
  rule inherits that behavior directly. A caller wanting "lowercase or
  no letters at all" should compose explicitly
  (`is_lowercase | negate(is_alpha)` or similar), not assume it here.
* **Digits/Punctuation Don't Break It:**
  `"hello123".islower()` is `True` — only *cased* characters are
  checked; digits and punctuation are simply ignored by the underlying
  Python method, not treated as violations.

---

## 2. Relationship to Sibling Rules

See `IsAlpha.py`'s design notes, section 2 — same shared shape and
rationale for keeping these as independent, one-rule-per-file classes.
`IsLowercase`/`IsUppercase` are mirror images of each other, same
relationship as `IsEven`/`IsOdd` — independent implementations, not one
derived via `Not()` from the other.

---

## 3. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at
  all; `ValueError` (`IS_LOWERCASE_ERROR`) when it is a string but has an
  uppercase character or no cased characters at all.
"""
