"""Tests for the IsHashable rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import IsHashable


class UnhashableClass:
    __hash__ = None  # type: ignore


def test_is_hashable_contract(subtests):
    """Verify the complete contract of the IsHashable rule."""
    rule = IsHashable()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[123, "text", (1, 2), True, None, float],
        invalid_values=[[1, 2], {"a": 1}, {1, 2}, UnhashableClass()],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_hashable_exception(subtests):
    """Verify diagnosis (TypeError) when value is not hashable."""
    rule = IsHashable()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([1, 2, 3], Kwargs(value_name="key")),
        exception_type=ValidationError,
        label="key",
        value=[1, 2, 3],
        error_name="IS_HASHABLE_ERROR",
        expected="hashable value",
        problem="Value [1, 2, 3] of type 'list' is not hashable.",
        how_to_fix="Provide a hashable value (e.g. immutable types like int, str, tuple; avoid list, dict, set).",
        exception=TypeError,
        verbose=False,
    )