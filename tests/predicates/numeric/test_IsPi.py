"""Tests for the IsPi rule."""

from decimal import Decimal
import math
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsPi


def test_is_pi_contract(subtests):
    """Verify the complete contract of the IsPi rule."""
    # For 2 decimal places, math.pi rounds to 3.14
    rule = IsPi(decimal_places=2)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[3.14, 3.14159, Decimal("3.14")],
        invalid_values=[3.1, 3.15, 3.0, "3.14", True, None, []],
        invalid_init_params=[
            ((-1,), {}),       # Negative decimal places -> ParamError
            ((1.5,), {}),      # Float in init -> ParamError
            (("2",), {}),      # String in init -> ParamError
            ((True,), {}),     # Boolean in init -> ParamError
        ],
        deep_check=True,
        verbose=False,
    )


def test_is_pi_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when non-numeric type is passed."""
    rule = IsPi(decimal_places=4)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("3.1416", Kwargs(value_name="pi_val")),
        exception_type=ValidationError,
        label="pi_val",
        value="3.1416",
        error_name="IS_PI_ERROR",
        expected="3.1416 (math.pi to 4 decimals)",
        problem="Value '3.1416' of type 'str' is not a numeric value.",
        how_to_fix="Provide a numeric value that rounds to 3.1416 at 4 decimal places.",
        exception=TypeError,
        verbose=False,
    )


def test_is_pi_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when value does not match Pi after rounding."""
    rule = IsPi(decimal_places=2)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(3.55, Kwargs(value_name="pi_val")),
        exception_type=ValidationError,
        label="pi_val",
        value=3.55,
        error_name="IS_PI_ERROR",
        expected="3.14 (math.pi to 2 decimals)",
        problem="Value 3.55 rounds to 3.55, expected 3.14.",
        how_to_fix="Provide a value that rounds to 3.14 at 2 decimal places.",
        exception=ValueError,
        verbose=False,
    )