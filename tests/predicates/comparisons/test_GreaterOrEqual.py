"""Tests for the GreaterOrEqual comparison rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.comparisons import GreaterOrEqual


def test_greater_or_equal_contract(subtests):
    """Verify the contract of the GreaterOrEqual rule."""
    rule = GreaterOrEqual(10)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[10, 11, 10.0, 100],
        invalid_values=[9.9, 9, 0, -5, "10", None, [10]],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_greater_or_equal_out_of_bounds_exception(subtests):
    """Verify diagnosis (ValueError) when value is strictly less than the threshold."""
    rule = GreaterOrEqual(10)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(5, Kwargs(value_name="age")),
        exception_type=ValidationError,
        label="age",
        value=5,
        error_name="GREATER_OR_EQUAL_ERROR",
        expected="value greater than or equal to 10",
        problem="Value 5 is less than 10.",
        how_to_fix="Provide a value greater than or equal to 10.",
        exception=ValueError,
        verbose=False,
    )


def test_greater_or_equal_incomparable_type_exception(subtests):
    """Verify diagnosis (TypeError) when input type cannot be compared to the threshold."""
    rule = GreaterOrEqual(10)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("text", Kwargs(value_name="age")),
        exception_type=ValidationError,
        label="age",
        value="text",
        error_name="GREATER_OR_EQUAL_ERROR",
        expected="value greater than or equal to 10",
        problem="Cannot compare 'str' ('text') with 'int' (10).",
        how_to_fix="Provide a value of a type comparable with 'int'.",
        exception=TypeError,
    )