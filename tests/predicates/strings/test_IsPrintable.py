"""Tests for the IsPrintable rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsPrintable, is_printable


def test_is_printable_contract(subtests):
    """Verify the complete contract of the IsPrintable rule."""
    rule = IsPrintable()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["hello world", "abc 123 !@#", "Příliš žluťoučký kůň", ""],
        invalid_values=["hello\x00world", "line1\x01line2", 123, None, True, []],
        deep_check=True,
        verbose=False,
    )


def test_is_printable_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsPrintable()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(None, Kwargs(value_name="text")),
        exception_type=ValidationError,
        label="text",
        value=None,
        error_name="IS_PRINTABLE_ERROR",
        expected="a printable string (no control characters)",
        problem="Value None of type 'NoneType' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_printable_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string contains unprintable characters."""
    rule = IsPrintable()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("hello\x00world", Kwargs(value_name="text")),
        exception_type=ValidationError,
        label="text",
        value="hello\x00world",
        error_name="IS_PRINTABLE_ERROR",
        expected="a printable string (no control characters)",
        problem="Value 'hello\\x00world' contains unprintable or control characters.",
        how_to_fix="Provide a string containing only printable characters.",
        exception=ValueError,
        verbose=False,
    )


def test_is_printable_helper(subtests):
    """Verify helper predicate function is_printable."""
    with subtests.test("is_printable_helper"):
        assert is_printable("Clean text") is True
        assert is_printable("Text\x00WithNull") is False
        assert is_printable(123) is False