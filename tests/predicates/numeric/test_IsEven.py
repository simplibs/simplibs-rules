"""Tests for the IsEven rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsEven


def test_is_even_contract(subtests):
    """Verify the complete contract of the IsEven rule."""
    rule = IsEven()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[0, 2, -4, 100, -100],
        invalid_values=[1, -3, 99, 2.0, -4.0, True, False, "2", None, []],
        deep_check=True,
        verbose=False,
    )


def test_is_even_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when non-integer type is passed."""
    rule = IsEven()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(2.0, Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        value=2.0,
        error_name="IS_EVEN_ERROR",
        expected="an even integer",
        problem="Value 2.0 of type 'float' is not an integer.",
        how_to_fix="Provide an integer value (booleans like True/False are excluded).",
        exception=TypeError,
        verbose=False,
    )


def test_is_even_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when value is an odd integer."""
    rule = IsEven()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(3, Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        value=3,
        error_name="IS_EVEN_ERROR",
        expected="an even integer",
        problem="Value 3 is an odd integer.",
        how_to_fix="Provide an even integer (e.g. -2, 0, 4).",
        exception=ValueError,
        verbose=False,
    )