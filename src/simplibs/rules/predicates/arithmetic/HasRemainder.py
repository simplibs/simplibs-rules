from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from ..numeric.IsInteger import is_integer
from .._init_validators import (
    validate_param_is_integer,
    validate_param_is_not_zero,
    validate_param_remainder_in_range,
)


class HasRemainder(Rule):
    """Value must give the specified remainder when divided by divisor.

    Rule:
        value % divisor == remainder

    Example:
        validate(value, HasRemainder(divisor=3, remainder=1))
    """

    __slots__ = ("divisor", "remainder")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, divisor: int, remainder: int) -> None:

        # 1. Parameter validation
        if not (
            is_integer(divisor)
            and divisor != 0
            and is_integer(remainder)
            and 0 <= remainder < abs(divisor)
        ):
            validate_param_is_integer("HasRemainder", "divisor", divisor)
            validate_param_is_not_zero("HasRemainder", "divisor", divisor)
            validate_param_is_integer("HasRemainder", "remainder", remainder)
            validate_param_remainder_in_range("HasRemainder", divisor, remainder)

        # 2. Parameter assignment
        self.divisor = divisor
        self.remainder = remainder

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is an int and matches the required remainder
        return (

            # 1.1 Check that the value is of type int (excluding bool)
            isinstance(value, int)
            and not isinstance(value, bool)

            # 1.2 Check that it matches the required remainder
            and value % self.divisor == self.remainder
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

        # 1.2 When the value does not have the required remainder
        else:
            actual_remainder = value % self.divisor
            problem = (
                f"Value {value!r} has remainder {actual_remainder} "
                f"when divided by {self.divisor}, but expected {self.remainder}."
            )
            how_to_fix = (
                f"Provide an integer 'n' where n % {self.divisor} == {self.remainder} "
                f"(e.g., {self.remainder}, {self.remainder + abs(self.divisor)})."
            )
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="HAS_REMAINDER_ERROR",
            label=value_name,
            expected=f"remainder {self.remainder} when divided by {self.divisor}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# HasRemainder — Modular Arithmetic Remainder Validation Rule

## Purpose
The `HasRemainder` rule checks whether an integer input value leaves a
specific remainder when divided by a target divisor
(`value % divisor == remainder`).

---

## 1. Execution Rationale & Fail-Fast Safeguards

* **Constructor Parameter Guard:**
  `__init__` performs a joint check validating that `divisor` is a non-zero
  integer, `remainder` is an integer, and `0 <= remainder < |divisor|`. On
  failure, it delegates sequentially to parameter validation helpers to
  raise a targeted `ParamError`.
* **Strict Integer Type Safeguard:**
  In `is_valid`, non-integer inputs fail immediately (`return False`) using
  `is_integer`. In `build_exception`, non-integers assemble a `TypeError`
  directly using internal branching.

---

## 2. Exception Card Design

* **Type Failures:** Evaluated non-integer inputs format problem/fix
  strings as `TypeError`.
* **Remainder Failures:** Evaluated inputs that fail remainder checks
  format problem/fix strings as `ValueError` (`HAS_REMAINDER_ERROR`),
  displaying both the actual evaluated remainder (`value % divisor`) and
  the expected remainder.
"""
