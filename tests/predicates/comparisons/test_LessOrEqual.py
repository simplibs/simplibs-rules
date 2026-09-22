"""Tests for the LessOrEqual comparison rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.comparisons import LessOrEqual


def test_less_or_equal_contract(subtests):
    """Verify the contract of the LessOrEqual rule."""
    rule = LessOrEqual(100)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[100, 99, 0, -10, 100.0],
        invalid_values=[100.1, 101, 150, "50", None, [50]],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_less_or_equal_out_of_bounds_exception(subtests):
    """Verify diagnosis (ValueError) when value is strictly greater than the threshold."""
    rule = LessOrEqual(100)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(150, Kwargs(value_name="speed")),
        exception_type=ValidationError,
        label="speed",
        value=150,
        error_name="LESS_OR_EQUAL_ERROR",
        expected="value less than or equal to 100",
        problem="Value 150 is greater than 100.",
        how_to_fix="Provide a value less than or equal to 100.",
        exception=ValueError,
    )


def test_less_or_equal_incomparable_type_exception(subtests):
    """Verify diagnosis (TypeError) when input type cannot be compared to the threshold."""
    rule = LessOrEqual(100)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("text", Kwargs(value_name="speed")),
        exception_type=ValidationError,
        label="speed",
        value="text",
        error_name="LESS_OR_EQUAL_ERROR",
        expected="value less than or equal to 100",
        problem="Cannot compare 'str' ('text') with 'int' (100).",
        how_to_fix="Provide a value of a type comparable with 'int'.",
        exception=TypeError,
    )