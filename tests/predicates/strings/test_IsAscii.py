"""Tests for the IsAscii rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsAscii


def test_is_ascii_contract(subtests):
    """Verify the complete contract of the IsAscii rule."""
    rule = IsAscii()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["", "hello", "123", "a-b_c!", "line\nbreak"],
        invalid_values=["příliš", "česky", "€", "©", 123, None, True],
        deep_check=True,
        verbose=False,
    )


def test_is_ascii_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsAscii()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="text")),
        exception_type=ValidationError,
        label="text",
        value=123,
        error_name="IS_ASCII_ERROR",
        expected="a purely ASCII string",
        problem="Value 123 of type 'int' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_ascii_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string contains non-ASCII characters."""
    rule = IsAscii()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("příliš", Kwargs(value_name="text")),
        exception_type=ValidationError,
        label="text",
        value="příliš",
        error_name="IS_ASCII_ERROR",
        expected="a purely ASCII string",
        problem="Value 'příliš' contains non-ASCII characters.",
        how_to_fix="Provide a string containing only ASCII characters (U+0000-U+007F).",
        exception=ValueError,
        verbose=False,
    )