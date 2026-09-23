"""Tests for the IsString rule and its helper functions."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings.IsString import (
    IsString,
    is_string,
    is_non_empty_string,
)


def test_is_string_contract(subtests):
    """Verify the complete contract of the IsString rule."""
    rule = IsString()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["", "hello", "123", "   "],
        invalid_values=[123, 10.5, True, None, [], {}],
        deep_check=True,
        verbose=False,
    )


def test_is_string_exception(subtests):
    """Verify diagnosis (TypeError) when non-string value is passed."""
    rule = IsString()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(100, Kwargs(value_name="username")),
        exception_type=ValidationError,
        label="username",
        value=100,
        error_name="IS_STRING_ERROR",
        expected="a string",
        problem="Value 100 of type 'int' is not a string.",
        how_to_fix="Provide a str value.",
        exception=TypeError,
    )


def test_is_string_helpers(subtests):
    """Verify helper module functions is_string and is_non_empty_string."""
    with subtests.test("is_string_helper"):
        assert is_string("text") is True
        assert is_string("") is True
        assert is_string(123) is False

    with subtests.test("is_non_empty_string_helper"):
        assert is_non_empty_string("text") is True
        assert is_non_empty_string("  text  ") is True
        assert is_non_empty_string("") is False
        assert is_non_empty_string("   ") is False
        assert is_non_empty_string(123) is False