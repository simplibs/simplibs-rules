"""Tests for the IsIterable rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import IsIterable


def test_is_iterable_contract(subtests):
    """Verify the complete contract of the IsIterable rule."""
    rule = IsIterable()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["text", [1, 2], (1, 2), {"a": 1}, {1, 2}, (x for x in range(3))],
        invalid_values=[123, 3.14, True, None],
        deep_check=True,
        verbose=False,
    )


def test_is_iterable_exception(subtests):
    """Verify diagnosis (TypeError) when value is not iterable."""
    rule = IsIterable()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="items")),
        exception_type=ValidationError,
        label="items",
        value=123,
        error_name="IS_ITERABLE_ERROR",
        expected="iterable value",
        problem="Value 123 of type 'int' is not iterable.",
        how_to_fix="Provide an iterable object (e.g. list, tuple, set, dict, generator, or string).",
        exception=TypeError,
        verbose=False,
    )