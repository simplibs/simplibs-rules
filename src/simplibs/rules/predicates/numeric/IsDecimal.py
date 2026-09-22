from typing import Any
from decimal import Decimal
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsDecimal(Rule):
    """Value must be a decimal.Decimal.

    Rule:
        isinstance(value, Decimal)

    Example:
        validate(value, IsDecimal())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is exactly of type Decimal
        return isinstance(value, Decimal)

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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not a Decimal."
        how_to_fix = "Provide a decimal.Decimal value (e.g. Decimal('10.5'))."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_DECIMAL_ERROR",
            label=value_name,
            expected="decimal.Decimal",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsDecimal — Exact Decimal Type Validation Rule

## Purpose
The `IsDecimal` rule validates that an input value is strictly an instance
of Python's standard `decimal.Decimal`.

---

## 1. Execution Rationale & Safeguards

* **Exact Instance Match:**
  Uses direct `isinstance(value, Decimal)`. Integers, floats, and strings
  are explicitly rejected to protect financial and exact-precision domain
  workflows.
* **Zero Exception Risk:**
  `isinstance` evaluation is safe and guaranteed not to raise runtime
  exceptions.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_DECIMAL_ERROR` wrapping a
  `TypeError`.
* **Fix Guidance:** Recommends constructing a `Decimal` instance (e.g.
  using string representations like `Decimal('10.5')`).
"""
