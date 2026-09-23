"""Tests for the IsCallable rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import IsCallable


class CallableClass:
    def __call__(self) -> None:
        pass


def test_is_callable_contract(subtests):
    """Verify the complete contract of the IsCallable rule."""
    rule = IsCallable()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            print,
            lambda x: x,
            CallableClass(),
            int,
            str.upper,
        ],
        invalid_values=[123, "text", [1, 2], {"a": 1}, None, 3.14],
        deep_check=True,
        verbose=False,
    )


def test_is_callable_exception(subtests):
    """Verify diagnosis (TypeError) when value is not callable."""
    rule = IsCallable()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("not_callable", Kwargs(value_name="callback")),
        exception_type=ValidationError,
        label="callback",
        value="not_callable",
        error_name="IS_CALLABLE_ERROR",
        expected="callable object",
        problem="Value 'not_callable' of type 'str' is not callable.",
        how_to_fix="Provide a callable (function, method, lambda, or object implementing __call__).",
        exception=TypeError,
        verbose=False,
    )