"""Tests for the IsAlpha rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsAlpha


def test_is_alpha_contract(subtests):
    """Verify the complete contract of the IsAlpha rule."""
    rule = IsAlpha()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["abc", "Hello", "Příliš"],
        invalid_values=["", "abc1", "hello world", "a-b", 123, None, True],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_alpha_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsAlpha()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(None, Kwargs(value_name="name")),
        exception_type=ValidationError,
        label="name",
        value=None,
        error_name="IS_ALPHA_ERROR",
        expected="a non-empty, purely alphabetic string",
        problem="Value None of type 'NoneType' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_alpha_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string contains non-alphabetic characters or is empty."""
    rule = IsAlpha()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("abc123", Kwargs(value_name="name")),
        exception_type=ValidationError,
        label="name",
        value="abc123",
        error_name="IS_ALPHA_ERROR",
        expected="a non-empty, purely alphabetic string",
        problem="Value 'abc123' contains non-alphabetic characters or is empty.",
        how_to_fix="Provide a non-empty string containing only alphabetic characters.",
        exception=ValueError,
        verbose=False,
    )