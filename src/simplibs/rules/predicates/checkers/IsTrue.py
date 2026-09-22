from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsTrue(Rule):
    """Value must be the literal boolean True (not just truthy).

    Rule:
        value is True

    Example:
        validate(value, IsTrue())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate identity
        return value is True

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
        problem = f"Value is not True (got {value!r})."
        how_to_fix = "Provide the literal boolean value True."
        exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_TRUE_ERROR",
            label=value_name,
            expected="True",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsTrue — Literal Boolean True Identity Validation Rule

## Purpose
The `IsTrue` rule validates that an input value is strictly the singleton
boolean object `True`.

---

## 1. Execution Rationale & Strict Identity Checks

* **Strict Identity over Truthiness:**
  Evaluates identity via `value is True`. Truthy non-boolean values (`1`,
  `"hello"`, `[1]`) are explicitly rejected to enforce type purity.
* **Zero Exception Overhead:**
  Identity checking (`is`) is guaranteed to be safe and free of exceptions
  in standard Python execution.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_TRUE_ERROR` wrapping a `ValueError`.
* **Fix Guidance:** Clear instruction specifying the boolean literal
  `True`.
"""
