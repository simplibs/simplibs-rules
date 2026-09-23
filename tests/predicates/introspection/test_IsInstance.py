"""Tests for the IsInstance rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import IsInstance


def test_is_instance_contract(subtests):
    """Verify the complete contract of the IsInstance rule."""
    rule = IsInstance(int, str)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[123, "text", True],  # bool is a subclass of int in Python
        invalid_values=[3.14, [1, 2], None, {"a": 1}],
        invalid_init_params=[
            ((), {}),             # No type in constructor -> ParamError
            ((123,), {}),         # Passed parameter is not a type -> ParamError
            ((int, "str"), {}),   # One parameter is not a type -> ParamError
        ],
        deep_check=True,
        verbose=False,
    )


def test_is_instance_exception(subtests):
    """Verify diagnosis (TypeError) when value is not an instance of expected type."""
    rule = IsInstance(int, float)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("text", Kwargs(value_name="amount")),
        exception_type=ValidationError,
        label="amount",
        value="text",
        error_name="IS_INSTANCE_ERROR",
        expected="instance of (int, float)",
        problem="Value 'text' is of type 'str', expected instance of (int, float).",
        how_to_fix="Provide an instance of (int, float).",
        exception=TypeError,
        verbose=False,
    )