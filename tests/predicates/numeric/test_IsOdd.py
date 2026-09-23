"""Tests for the IsOdd rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsOdd


def test_is_odd_contract(subtests):
    """Verify the complete contract of the IsOdd rule."""
    rule = IsOdd()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, -1, 3, -5, 99],
        invalid_values=[0, 2, -4, 1.0, -3.0, True, False, "1", None, []],
        deep_check=True,
        verbose=False,
    )


def test_is_odd_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when non-integer type is passed."""
    rule = IsOdd()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(1.0, Kwargs(value_name="item_count")),
        exception_type=ValidationError,
        label="item_count",
        value=1.0,
        error_name="IS_ODD_ERROR",
        expected="an odd integer",
        problem="Value 1.0 of type 'float' is not an integer.",
        how_to_fix="Provide an integer value (booleans like True/False are excluded).",
        exception=TypeError,
        verbose=False,
    )


def test_is_odd_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when value is an even integer."""
    rule = IsOdd()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(4, Kwargs(value_name="item_count")),
        exception_type=ValidationError,
        label="item_count",
        value=4,
        error_name="IS_ODD_ERROR",
        expected="an odd integer",
        problem="Value 4 is an even integer.",
        how_to_fix="Provide an odd integer (e.g. -3, 1, 5).",
        exception=ValueError,
        verbose=False,
    )