"""Tests for the IsBlank rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsBlank


def test_is_blank_contract(subtests):
    """Verify the complete contract of the IsBlank rule."""
    rule = IsBlank()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["", " ", "   ", "\t", "\n", " \t\n "],
        invalid_values=["hello", " a ", "123", 123, None, True, []],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_blank_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when value is not a string."""
    rule = IsBlank()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="note")),
        exception_type=ValidationError,
        label="note",
        value=123,
        error_name="IS_BLANK_ERROR",
        expected="empty or whitespace-only string",
        problem="Value 123 of type 'int' is not a string.",
        how_to_fix="Provide an empty string or a string containing only whitespace.",
        exception=TypeError,
        verbose=False,
    )


def test_is_blank_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string contains visible characters/text."""
    rule = IsBlank()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("text", Kwargs(value_name="note")),
        exception_type=ValidationError,
        label="note",
        value="text",
        error_name="IS_BLANK_ERROR",
        expected="empty or whitespace-only string",
        problem="Value 'text' contains non-whitespace characters.",
        how_to_fix="Provide an empty string or a string containing only whitespace.",
        exception=ValueError,
        verbose=False,
    )