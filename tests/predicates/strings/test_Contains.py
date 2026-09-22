"""Tests for the Contains rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import Contains


def test_contains_contract(subtests):
    """Verify the complete contract of the Contains rule."""
    rule = Contains("@")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["user@domain.com", "abc@def", "@"],
        invalid_values=["userdomain.com", "hello", "", 123, None, True, []],
        invalid_init_params=[
            ((123,), {}),       # Non-string parameter -> ParamError
            ((None,), {}),      # None parameter -> ParamError
            ((True,), {}),      # Boolean parameter -> ParamError
            (([],), {}),        # List parameter -> ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_contains_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = Contains("@")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(12345, Kwargs(value_name="email")),
        exception_type=ValidationError,
        label="email",
        value=12345,
        error_name="CONTAINS_ERROR",
        expected="string containing '@'",
        problem="Value 12345 of type 'int' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_contains_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string does not contain the required substring."""
    rule = Contains("@")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("user.domain.com", Kwargs(value_name="email")),
        exception_type=ValidationError,
        label="email",
        value="user.domain.com",
        error_name="CONTAINS_ERROR",
        expected="string containing '@'",
        problem="Value 'user.domain.com' does not contain '@'.",
        how_to_fix="Provide a string containing '@'.",
        exception=ValueError,
        verbose=False,
    )