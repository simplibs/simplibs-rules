"""Tests for the GreaterThan comparison rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.comparisons import GreaterThan


def test_greater_than_contract(subtests):
    """Verify the contract of the GreaterThan rule."""
    rule = GreaterThan(10)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[11, 15, 10.1, 100],
        invalid_values=[10, 5, 0, -5, "15", None, [10]],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_greater_than_out_of_bounds_exception(subtests):
    """Verify diagnosis (ValueError) when value is less than or equal to the threshold."""
    rule = GreaterThan(10)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(5, Kwargs(value_name="score")),
        exception_type=ValidationError,
        label="score",
        value=5,
        error_name="GREATER_THAN_ERROR",
        expected="value greater than 10",
        problem="Value 5 is not greater than 10.",
        how_to_fix="Provide a value strictly greater than 10.",
        exception=ValueError,
        verbose=False,
    )


def test_greater_than_incomparable_type_exception(subtests):
    """Verify diagnosis (TypeError) when input type cannot be compared to the threshold."""
    rule = GreaterThan(10)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("text", Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        value="text",
        error_name="GREATER_THAN_ERROR",
        expected="value greater than 10",
        problem="Cannot compare 'str' ('text') with 'int' (10).",
        how_to_fix="Provide a value of a type comparable with 'int'.",
        exception=TypeError,
    )