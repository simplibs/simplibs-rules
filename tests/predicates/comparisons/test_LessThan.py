"""Tests for the LessThan comparison rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.comparisons import LessThan


def test_less_than_contract(subtests):
    """Verify the contract of the LessThan rule."""
    rule = LessThan(100)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[99, 0, -10, 99.9],
        invalid_values=[100, 101, 150, "50", None, [50]],
        deep_check=True,
        verbose=False,
    )


def test_less_than_out_of_bounds_exception(subtests):
    """Verify diagnosis (ValueError) when value is greater than or equal to threshold."""
    rule = LessThan(100)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(150, Kwargs(value_name="percentage")),
        exception_type=ValidationError,
        label="percentage",
        value=150,
        error_name="LESS_THAN_ERROR",
        expected="value less than 100",
        problem="Value 150 is not less than 100.",
        how_to_fix="Provide a value strictly less than 100.",
        exception=ValueError,
        verbose=False,
    )


def test_less_than_incomparable_type_exception(subtests):
    """Verify diagnosis (TypeError) when input type cannot be compared to the threshold."""
    rule = LessThan(100)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("text", Kwargs(value_name="percentage")),
        exception_type=ValidationError,
        label="percentage",
        value="text",
        error_name="LESS_THAN_ERROR",
        expected="value less than 100",
        problem="Cannot compare 'str' ('text') with 'int' (100).",
        how_to_fix="Provide a value of a type comparable with 'int'.",
        exception=TypeError,
    )