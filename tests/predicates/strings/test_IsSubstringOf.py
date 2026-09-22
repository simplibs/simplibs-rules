"""Tests for the IsSubstringOf rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsSubstringOf


def test_is_substring_of_contract(subtests):
    """Verify the complete contract of the IsSubstringOf rule."""
    rule = IsSubstringOf("ADMIN_ROLE_FULL_ACCESS")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["ADMIN", "ROLE", "FULL_ACCESS", "ADMIN_ROLE_FULL_ACCESS", ""],
        invalid_values=["USER", "GUEST", "admin", 123, None, True, []],
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


def test_is_substring_of_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsSubstringOf("ADMIN_ROLE_FULL_ACCESS")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(12345, Kwargs(value_name="role")),
        exception_type=ValidationError,
        label="role",
        value=12345,
        error_name="IS_SUBSTRING_OF_ERROR",
        expected="substring of 'ADMIN_ROLE_FULL_ACCESS'",
        problem="Value 12345 of type 'int' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_substring_of_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string is not a substring of target string."""
    rule = IsSubstringOf("ADMIN_ROLE_FULL_ACCESS")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("GUEST", Kwargs(value_name="role")),
        exception_type=ValidationError,
        label="role",
        value="GUEST",
        error_name="IS_SUBSTRING_OF_ERROR",
        expected="substring of 'ADMIN_ROLE_FULL_ACCESS'",
        problem="Value 'GUEST' is not a substring of 'ADMIN_ROLE_FULL_ACCESS'.",
        how_to_fix="Provide a string that is contained within 'ADMIN_ROLE_FULL_ACCESS'.",
        exception=ValueError,
        verbose=False,
    )