from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsNone(Rule):
    """Value must be None.

    Rule:
        value is None

    Example:
        validate(value, IsNone())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate identity
        return value is None

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
        problem = f"Value is not None (got {value!r})."
        how_to_fix = "Provide None."
        exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_NONE_ERROR",
            label=value_name,
            expected="None",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsNone — Explicit None Singleton Validation Rule

## Purpose
The `IsNone` rule validates that an input value is strictly the `None`
singleton object.

---

## 1. Execution Rationale & Identity Verification

* **Strict Identity Check:**
  Evaluates identity via `value is None`. Non-None values (including falsy
  ones like `0`, `False`, `""`, `[]`) return `False`.
* **Interaction with `accept_none` Configuration:**
  When executing inside high-level functions where `accept_none=True`,
  `None` values trigger an early success short-circuit. Unit tests MUST
  verify `IsNone` with `accept_none=False` to ensure direct `is_valid`
  coverage.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_NONE_ERROR` wrapping a `ValueError`.
* **Fix Guidance:** Clear instruction requiring `None`.
"""
