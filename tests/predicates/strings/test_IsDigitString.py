"""Tests for the IsDigitString rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsDigitString


def test_is_digit_string_contract(subtests):
    """Verify the complete contract of the IsDigitString rule."""
    rule = IsDigitString()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["123", "007", "0"],
        invalid_values=["", "12.3", "-5", "123a", "abc", 123, None, True],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_digit_string_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsDigitString()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="pin")),
        exception_type=ValidationError,
        label="pin",
        value=123,
        error_name="IS_DIGIT_STRING_ERROR",
        expected="a non-empty, purely numeric-digit string",
        problem="Value 123 of type 'int' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_digit_string_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string contains non-digit characters or is empty."""
    rule = IsDigitString()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("12a3", Kwargs(value_name="pin")),
        exception_type=ValidationError,
        label="pin",
        value="12a3",
        error_name="IS_DIGIT_STRING_ERROR",
        expected="a non-empty, purely numeric-digit string",
        problem="Value '12a3' contains non-digit characters or is empty.",
        how_to_fix="Provide a non-empty string containing only digit characters.",
        exception=ValueError,
        verbose=False,
    )