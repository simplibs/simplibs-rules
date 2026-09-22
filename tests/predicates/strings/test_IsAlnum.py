"""Tests for the IsAlnum rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsAlnum


def test_is_alnum_contract(subtests):
    """Verify the complete contract of the IsAlnum rule."""
    rule = IsAlnum()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["abc", "123", "a1b2c3", "Python3"],
        invalid_values=["", "hello world", "a-b", "test!", 123, None, True, []],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_alnum_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsAlnum()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(12345, Kwargs(value_name="code")),
        exception_type=ValidationError,
        label="code",
        value=12345,
        error_name="IS_ALNUM_ERROR",
        expected="a non-empty, purely alphanumeric string",
        problem="Value 12345 of type 'int' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_alnum_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string contains non-alphanumeric characters or is empty."""
    rule = IsAlnum()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("hello-world", Kwargs(value_name="code")),
        exception_type=ValidationError,
        label="code",
        value="hello-world",
        error_name="IS_ALNUM_ERROR",
        expected="a non-empty, purely alphanumeric string",
        problem="Value 'hello-world' contains non-alphanumeric characters or is empty.",
        how_to_fix="Provide a non-empty string containing only letters and digits.",
        exception=ValueError,
        verbose=False,
    )