"""Tests for the IsLowercase rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsLowercase


def test_is_lowercase_contract(subtests):
    """Verify the complete contract of the IsLowercase rule."""
    rule = IsLowercase()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["hello", "hello123", "a-b-c!"],
        invalid_values=["", "123", "Hello", "HELLO", "hello World", 123, None, True],
        deep_check=True,
        verbose=False,
    )


def test_is_lowercase_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsLowercase()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(None, Kwargs(value_name="username")),
        exception_type=ValidationError,
        label="username",
        value=None,
        error_name="IS_LOWERCASE_ERROR",
        expected="an entirely lowercase string",
        problem="Value None of type 'NoneType' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_lowercase_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string contains uppercase characters or has no cased characters."""
    rule = IsLowercase()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("User", Kwargs(value_name="username")),
        exception_type=ValidationError,
        label="username",
        value="User",
        error_name="IS_LOWERCASE_ERROR",
        expected="an entirely lowercase string",
        problem="Value 'User' contains an uppercase character or has no cased characters.",
        how_to_fix="Provide a string that is entirely lowercase (with at least one letter).",
        exception=ValueError,
        verbose=False,
    )