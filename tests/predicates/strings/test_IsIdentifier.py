"""Tests for the IsIdentifier rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsIdentifier, is_identifier


def test_is_identifier_contract(subtests):
    """Verify the complete contract of the IsIdentifier rule."""
    rule = IsIdentifier()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["var_name", "myFunc1", "_private", "CLASS", "def"],
        invalid_values=["", "123var", "var-name", "var name", 123, None, True, []],
        deep_check=True,
        verbose=False,
    )


def test_is_identifier_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsIdentifier()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(12345, Kwargs(value_name="var_name")),
        exception_type=ValidationError,
        label="var_name",
        value=12345,
        error_name="IS_IDENTIFIER_ERROR",
        expected="a valid Python identifier string",
        problem="Value 12345 of type 'int' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_identifier_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string is not a valid Python identifier."""
    rule = IsIdentifier()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("123var", Kwargs(value_name="var_name")),
        exception_type=ValidationError,
        label="var_name",
        value="123var",
        error_name="IS_IDENTIFIER_ERROR",
        expected="a valid Python identifier string",
        problem="Value '123var' is not a valid Python identifier.",
        how_to_fix="Provide a valid Python identifier string (e.g. 'my_var', 'foo1').",
        exception=ValueError,
        verbose=False,
    )


def test_is_identifier_helper(subtests):
    """Verify helper predicate function is_identifier."""
    with subtests.test("is_identifier_helper"):
        assert is_identifier("valid_var") is True
        assert is_identifier("123invalid") is False
        assert is_identifier(123) is False