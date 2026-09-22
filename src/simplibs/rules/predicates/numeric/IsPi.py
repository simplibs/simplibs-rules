from typing import Any
import math
from decimal import Decimal
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import raise_param_not_non_negative_integer_error
# Inners
from .IsInteger import is_non_negative_integer
from .IsNumber import is_number


class IsPi(Rule):
    """Value must equal math.pi when rounded to `decimal_places` decimals.

    Rule:
        round(value, decimal_places) == round(math.pi, decimal_places)

    Example:
        validate(value, IsPi(decimal_places=5))
    """

    __slots__ = ("decimal_places", "_rounded_pi")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, decimal_places: int) -> None:

        # 1. Check that it's a non-negative integer (int >= 0)
        if not is_non_negative_integer(decimal_places):
            raise_param_not_non_negative_integer_error("IsPi", "decimal_places", decimal_places)

        # 2. Store parameters and precompute the rounded value of Pi
        self.decimal_places = decimal_places
        self._rounded_pi = round(math.pi, decimal_places)

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and the rounded value of Pi
        try:
            return (

                # 1.1 Check that the value is a supported numeric type (excluding bool)
                isinstance(value, (int, float, Decimal))
                and not isinstance(value, bool)

                # 1.2 Check that the rounded value matches the precomputed value of Pi
                # Cast to float ensures seamless Decimal and int comparison with _rounded_pi
                and round(float(value), self.decimal_places) == self._rounded_pi
            )

        # 2. Fallback for incomparable input (e.g. OverflowError or TypeError)
        except (TypeError, OverflowError, ValueError):
            return False

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
        # 1.1 If it's not a number
        if not is_number(value):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not a numeric value."
            how_to_fix = f"Provide a numeric value that rounds to {self._rounded_pi!r} at {self.decimal_places} decimal places."
            exception_type = TypeError
            expected = f"{self._rounded_pi!r} (math.pi to {self.decimal_places} decimals)"
        else:
            # 1.2 If it's a number, but doesn't match Pi after rounding
            try:
                rounded_val = round(float(value), self.decimal_places)
            except (TypeError, OverflowError, ValueError):
                rounded_val = value

            problem = f"Value {value!r} rounds to {rounded_val!r}, expected {self._rounded_pi!r}."
            how_to_fix = f"Provide a value that rounds to {self._rounded_pi!r} at {self.decimal_places} decimal places."
            exception_type = ValueError
            expected = f"{self._rounded_pi!r} (math.pi to {self.decimal_places} decimals)"

        # 2. Build the exception
        return ValidationError(
            error_name="IS_PI_ERROR",
            label=value_name,
            expected=expected,
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsPi — Pi Mathematical Constant Validation Rule

## Purpose
The `IsPi` rule validates that a numeric value matches `math.pi` up to a
user-specified precision (`decimal_places`).

---

## 1. Execution Rationale & Safeguards

* **Explicit Decimal Precision:**
  Requires explicit `decimal_places` (no default value) to prevent
  implicit rounding bugs.
* **Decimal & Numeric Coercion:**
  Casts `value` to `float(value)` during evaluation so that `Decimal` and
  `int` instances can be safely compared against float-precomputed `_rounded_pi`.
* **Constructor Fail-Fast Guards:**
  * Non-integer or boolean parameters trigger `ParamError`.
  * Negative decimal places trigger `ParamError`.
* **Precomputed Target Value:**
  Precomputes `round(math.pi, decimal_places)` once during initialization
  for high performance.
* **Dual Diagnostic Path (`build_exception`):**
  * `TypeError` when evaluated input is not a valid numeric type.
  * `ValueError` (`IS_PI_ERROR`) when numeric input does not round to the
    expected pi representation.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_PI_ERROR` wrapping a `ValueError`
  for numeric mismatch.
* **Fix Guidance:** Displays rounded target expectation and actual
  rounded value for transparent debugging.
"""