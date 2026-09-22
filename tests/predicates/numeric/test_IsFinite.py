"""Tests for the IsFinite rule."""

import math
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsFinite


def test_is_finite_contract(subtests):
    """Verify the complete contract of the IsFinite rule."""
    rule = IsFinite()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[0, 42, -100, 0.0, 3.14, -99.9],
        invalid_values=[
            float("inf"),
            float("-inf"),
            True,
            False,
            "123",
            None,
            [],
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_finite_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when non-primitive-numeric type is passed."""
    rule = IsFinite()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("42", Kwargs(value_name="val")),
        exception_type=ValidationError,
        label="val",
        value="42",
        error_name="IS_FINITE_ERROR",
        expected="a finite number (not NaN, not infinite)",
        problem="Value '42' of type 'str' is not a primitive number (int, float).",
        how_to_fix="Provide a primitive numeric value (int or float; booleans excluded).",
        exception=TypeError,
        verbose=False,
    )


def test_is_finite_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when number is infinite or NaN."""
    rule = IsFinite()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(float("inf"), Kwargs(value_name="val")),
        exception_type=ValidationError,
        label="val",
        value=float("inf"),
        error_name="IS_FINITE_ERROR",
        expected="a finite number (not NaN, not infinite)",
        problem="Value inf is not finite (NaN or infinite).",
        how_to_fix="Provide a finite numeric value (not NaN, not +/-inf).",
        exception=ValueError,
        verbose=False,
    )