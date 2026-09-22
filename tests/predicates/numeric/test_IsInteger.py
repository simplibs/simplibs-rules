"""Tests for the IsInteger rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric.IsInteger import (
    IsInteger,
    is_integer,
    is_non_negative_integer,
)


def test_is_integer_contract(subtests):
    """Verify the complete contract of the IsInteger rule."""
    rule = IsInteger()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[0, 10, -5],
        invalid_values=[10.5, "10", True, False, None, []],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_integer_exception(subtests):
    """Verify diagnosis (TypeError) on disallowed types (e.g. boolean)."""
    rule = IsInteger()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(True, Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        value=True,
        error_name="IS_INTEGER_ERROR",
        expected="an integer",
        problem="Value True of type 'bool' is not an integer.",
        how_to_fix="Provide an int value (booleans like True/False are excluded).",
        exception=TypeError,
        verbose=False,
    )


def test_is_integer_helpers():
    """Verify helper functions is_integer and is_non_negative_integer."""
    assert is_integer(5) is True
    assert is_integer(True) is False

    assert is_non_negative_integer(0) is True
    assert is_non_negative_integer(5) is True
    assert is_non_negative_integer(-1) is False
    assert is_non_negative_integer(True) is False