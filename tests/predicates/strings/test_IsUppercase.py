"""Tests for the IsUppercase rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsUppercase


def test_is_uppercase_contract(subtests):
    """Verify the complete contract of the IsUppercase rule."""
    rule = IsUppercase()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["HELLO", "HELLO123", "A-B-C!"],
        invalid_values=["", "123", "Hello", "hello", "HELLO World", 123, None, True],
        deep_check=True,
        verbose=False,
    )


def test_is_uppercase_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsUppercase()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="code")),
        exception_type=ValidationError,
        label="code",
        value=123,
        error_name="IS_UPPERCASE_ERROR",
        expected="an entirely uppercase string",
        problem="Value 123 of type 'int' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_uppercase_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string contains lowercase characters or has no cased characters."""
    rule = IsUppercase()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("Code", Kwargs(value_name="code")),
        exception_type=ValidationError,
        label="code",
        value="Code",
        error_name="IS_UPPERCASE_ERROR",
        expected="an entirely uppercase string",
        problem="Value 'Code' contains a lowercase character or has no cased characters.",
        how_to_fix="Provide a string that is entirely uppercase (with at least one letter).",
        exception=ValueError,
        verbose=False,
    )