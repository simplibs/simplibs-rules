"""Tests for the IsWhitespace rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsWhitespace, is_whitespace


def test_is_whitespace_contract(subtests):
    """Verify the complete contract of the IsWhitespace rule."""
    rule = IsWhitespace()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[" ", "   ", "\t", "\n", "\r\n", " \t\n "],
        invalid_values=["", "  a  ", "hello", "123", 123, None, True, []],
        deep_check=True,
        verbose=False,
    )


def test_is_whitespace_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsWhitespace()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(12345, Kwargs(value_name="padding")),
        exception_type=ValidationError,
        label="padding",
        value=12345,
        error_name="IS_WHITESPACE_ERROR",
        expected="a non-empty, purely whitespace string",
        problem="Value 12345 of type 'int' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_whitespace_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string contains non-whitespace characters or is empty."""
    rule = IsWhitespace()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("  a  ", Kwargs(value_name="padding")),
        exception_type=ValidationError,
        label="padding",
        value="  a  ",
        error_name="IS_WHITESPACE_ERROR",
        expected="a non-empty, purely whitespace string",
        problem="Value '  a  ' contains non-whitespace characters or is empty.",
        how_to_fix="Provide a non-empty string consisting only of whitespace characters.",
        exception=ValueError,
        verbose=False,
    )


def test_is_whitespace_helper(subtests):
    """Verify helper predicate function is_whitespace."""
    with subtests.test("is_whitespace_helper"):
        assert is_whitespace("   ") is True
        assert is_whitespace(" a ") is False
        assert is_whitespace("") is False
        assert is_whitespace(123) is False