"""Tests for the StartsWith rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import StartsWith


def test_starts_with_contract(subtests):
    """Verify the complete contract of the StartsWith rule."""
    rule = StartsWith("https://")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["https://example.com", "https://localhost", "https://"],
        invalid_values=["http://example.com", "ftp://example.com", "example.com", "", 123, None, True],
        invalid_init_params=[
            ((123,), {}),       # Non-string prefix -> ParamError
            ((None,), {}),      # None prefix -> ParamError
            ((True,), {}),      # Boolean prefix -> ParamError
            (([],), {}),        # List prefix -> ParamError
        ],
        deep_check=True,
        verbose=False,
    )


def test_starts_with_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = StartsWith("https://")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(404, Kwargs(value_name="url")),
        exception_type=ValidationError,
        label="url",
        value=404,
        error_name="STARTS_WITH_ERROR",
        expected="string starting with 'https://'",
        problem="Value 404 of type 'int' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_starts_with_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string does not start with the required prefix."""
    rule = StartsWith("https://")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("http://example.com", Kwargs(value_name="url")),
        exception_type=ValidationError,
        label="url",
        value="http://example.com",
        error_name="STARTS_WITH_ERROR",
        expected="string starting with 'https://'",
        problem="Value 'http://example.com' does not start with 'https://'.",
        how_to_fix="Provide a string starting with 'https://'.",
        exception=ValueError,
        verbose=False,
    )