"""Tests for the IsTitlecase rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import IsTitlecase


def test_is_titlecase_contract(subtests):
    """Verify the complete contract of the IsTitlecase rule."""
    rule = IsTitlecase()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["Hello World", "Python", "A Book Title 123"],
        invalid_values=["", "123", "hello world", "HELLO WORLD", "Hello world", 123, None, True],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_titlecase_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = IsTitlecase()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(None, Kwargs(value_name="title")),
        exception_type=ValidationError,
        label="title",
        value=None,
        error_name="IS_TITLECASE_ERROR",
        expected="a title-cased string",
        problem="Value None of type 'NoneType' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_is_titlecase_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string is not title-cased."""
    rule = IsTitlecase()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("hello world", Kwargs(value_name="title")),
        exception_type=ValidationError,
        label="title",
        value="hello world",
        error_name="IS_TITLECASE_ERROR",
        expected="a title-cased string",
        problem="Value 'hello world' is not title-cased.",
        how_to_fix="Provide a string where each word starts with an uppercase letter (e.g. 'Hello World').",
        exception=ValueError,
        verbose=False,
    )