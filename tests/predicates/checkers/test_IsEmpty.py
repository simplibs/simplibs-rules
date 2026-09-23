"""Tests for the IsEmpty checker rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.checkers import IsEmpty


def test_is_empty_contract(subtests):
    """Verify the complete contract of IsEmpty rule using master orchestrator."""
    rule = IsEmpty()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[[], {}, "", set(), tuple()],
        invalid_values=[[1], {"a": 1}, "text", {1}, (1,), 0, None, True],
        rule_factory=IsEmpty,
        deep_check=True,
        verbose=False,
    )


def test_is_empty_non_zero_length_exception(subtests):
    """Verify diagnosis (ValueError) when the object supports len() but is not empty."""
    rule = IsEmpty()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([1, 2], Kwargs(value_name="items")),
        exception_type=ValidationError,
        label="items",
        value=[1, 2],
        error_name="IS_EMPTY_ERROR",
        expected="empty container/collection",
        problem="Value [1, 2] has length 2, but expected length 0.",
        how_to_fix="Provide an empty container (e.g., [], {}, '', set()).",
        exception=ValueError,
        verbose=False,
    )


def test_is_empty_no_len_support_exception(subtests):
    """Verify diagnosis (TypeError) when the object does not support the len() interface."""
    rule = IsEmpty()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="number")),
        exception_type=ValidationError,
        label="number",
        value=123,
        error_name="IS_EMPTY_ERROR",
        expected="empty container/collection",
        problem="Value 123 of type 'int' does not support len().",
        how_to_fix="Provide a sized container or collection (e.g., list, dict, str, set).",
        exception=TypeError,
        verbose=False,
    )