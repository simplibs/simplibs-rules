"""Tests for the NotBlank rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import NotBlank


def test_not_blank_contract(subtests):
    """Verify the complete contract of the NotBlank rule."""
    rule = NotBlank()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["hello", " a ", "123", "text\nwith\nlines"],
        invalid_values=["", " ", "   ", "\t", "\n", 123, None, True, []],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_not_blank_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when value is not a string."""
    rule = NotBlank()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(None, Kwargs(value_name="code")),
        exception_type=ValidationError,
        label="code",
        value=None,
        error_name="NOT_BLANK_ERROR",
        expected="non-blank string",
        problem="Value None of type 'NoneType' is not a string.",
        how_to_fix="Provide a string with at least one non-whitespace character.",
        exception=TypeError,
        verbose=False,
    )


def test_not_blank_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string is empty or contains only whitespace."""
    rule = NotBlank()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("   ", Kwargs(value_name="code")),
        exception_type=ValidationError,
        label="code",
        value="   ",
        error_name="NOT_BLANK_ERROR",
        expected="non-blank string",
        problem="Value '   ' is empty or contains only whitespace.",
        how_to_fix="Provide a string with at least one non-whitespace character.",
        exception=ValueError,
        verbose=False,
    )