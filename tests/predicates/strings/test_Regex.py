"""Tests for the Regex rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import Regex


def test_regex_contract(subtests):
    """Verify the complete contract of the Regex rule."""
    rule = Regex(r"^[a-z]+$")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["hello", "abc", "z"],
        invalid_values=["Hello", "abc123", "", " ", 123, None, True],
        invalid_init_params=[
            ((123,), {}),       # Non-string parameter -> ParamError (TypeError)
            ((None,), {}),      # None parameter -> ParamError (TypeError)
            (("[a-z",), {}),    # Invalid regex syntax -> ParamError (re.error)
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_regex_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = Regex(r"^\d+$")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="zip_code")),
        exception_type=ValidationError,
        label="zip_code",
        value=123,
        error_name="REGEX_ERROR",
        expected="string matching pattern /^\\d+$/",
        problem="Value 123 of type 'int' is not a string.",
        how_to_fix="Provide a string matching pattern /^\\d+$/.",
        exception=TypeError,
        verbose=False,
    )


def test_regex_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string does not match the regular expression."""
    rule = Regex(r"^\d+$")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("abc", Kwargs(value_name="zip_code")),
        exception_type=ValidationError,
        label="zip_code",
        value="abc",
        error_name="REGEX_ERROR",
        expected="string matching pattern /^\\d+$/",
        problem="Value 'abc' does not match pattern /^\\d+$/.",
        how_to_fix="Ensure the string format matches regex pattern /^\\d+$/.",
        exception=ValueError,
        verbose=False,
    )