from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsFalse(Rule):
    """Value must be the literal boolean False (not just falsy).

    Rule:
        value is False

    Example:
        validate(value, IsFalse())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate identity
        return value is False

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
        problem = f"Value is not False (got {value!r})."
        how_to_fix = "Provide the literal boolean value False."
        exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_FALSE_ERROR",
            label=value_name,
            expected="False",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsFalse — Literal Boolean False Identity Validation Rule

## Purpose
The `IsFalse` rule validates that an input value is strictly the singleton
boolean object `False`.

---

## 1. Execution Rationale & Strict Identity Checks

* **Strict Identity over Truthiness:**
  Evaluates identity via `value is False`. Falsy non-boolean values (`0`,
  `""`, `[]`, `None`) are explicitly rejected to preserve strict type
  guarantees.
* **Deterministic Behavior:**
  Requires no exception guards in `is_valid` because identity checks
  (`is`) never raise exceptions in Python.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_FALSE_ERROR` wrapping a `ValueError`.
* **Fix Guidance:** Clear instruction specifying the boolean literal
  `False`.
"""
