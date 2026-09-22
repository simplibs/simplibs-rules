from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from ..numeric.IsInteger import is_integer
from .._init_validators import (
    validate_param_is_integer,
    validate_param_is_not_zero
)

class DivisibleBy(Rule):
    """Value must be evenly divisible by the given divisor.

    Rule:
        value % divisor == 0

    Example:
        validate(value, DivisibleBy(3))
    """

    __slots__ = ("divisor",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, divisor: int) -> None:

        # 1. Parameter validation
        if not (
            is_integer(divisor)
            and divisor != 0
        ):
            validate_param_is_integer("DivisibleBy", "divisor", divisor)
            validate_param_is_not_zero("DivisibleBy", "divisor", divisor)

        # 2. Parameter assignment
        self.divisor = divisor

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is an integer and evenly divisible by the divisor
        return (

            # 1.1 Check that the value is an int (excluding bool)
            isinstance(value, int)
            and not isinstance(value, bool)

            # 1.2 Check for even divisibility
            and value % self.divisor == 0
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
        # 1.1 When value is not a number
        if not is_integer(value):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not an integer."
            how_to_fix = "Provide an integer value."
            exception_type = TypeError

        # 1.2 When value is not divisible
        else:
            problem = f"Value {value!r} is not divisible by {self.divisor}."
            how_to_fix = f"Provide a multiple of {self.divisor} (e.g., {self.divisor}, {self.divisor * 2})."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="DIVISIBLE_BY_ERROR",
            label=value_name,
            expected=f"multiple of {self.divisor}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# DivisibleBy — Integer Divisibility Validation Rule

## Purpose
The `DivisibleBy` rule validates that an integer input value is evenly
divisible (`value % divisor == 0`) by a target divisor.

---

## 1. Execution Rationale & Strict Typing

* **Strict Integer Restriction:**
  Restricted exclusively to pure `int` types (excluding `bool`). Floats are
  intentionally rejected to prevent floating-point precision bugs in modulo
  arithmetic.
* **Constructor Protection (Fail-Fast):**
  `__init__` protects parameters via `is_integer` and `divisor != 0`. On
  failure, it delegates sequentially to `validate_param_is_integer` and
  `validate_param_is_not_zero` (`ParamError`).

---

## 2. Exception Card Design

* **Type Failures:** Evaluated non-integer inputs format problem/fix
  strings as `TypeError`.
* **Divisibility Failures:** Evaluated inputs that fail divisibility format
  problem/fix strings as `ValueError` (`DIVISIBLE_BY_ERROR`) with concrete
  examples of multiples.
"""
