"""Tests for the NotEmpty checker rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.checkers import NotEmpty


def test_not_empty_contract(subtests):
    """Verify the complete contract of NotEmpty rule using master orchestrator."""
    rule = NotEmpty()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[[1], {"a": 1}, "text", {1}, (1,)],
        invalid_values=[[], {}, "", set(), tuple(), 0, None, False],
        rule_factory=NotEmpty,
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_not_empty_zero_length_exception(subtests):
    """Verify diagnosis (ValueError) when container is empty (len == 0)."""
    rule = NotEmpty()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([], Kwargs(value_name="users")),
        exception_type=ValidationError,
        label="users",
        value=[],
        error_name="NOT_EMPTY_ERROR",
        expected="non-empty container/collection",
        problem="Value [] is empty (length is 0).",
        how_to_fix="Provide a container or collection with at least one element.",
        exception=ValueError,
        verbose=False,
    )


def test_not_empty_no_len_support_exception(subtests):
    """Verify diagnosis (TypeError) when the object does not support the len() interface."""
    rule = NotEmpty()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(None, Kwargs(value_name="data")),
        exception_type=ValidationError,
        label="data",
        value=None,
        error_name="NOT_EMPTY_ERROR",
        expected="non-empty container/collection",
        problem="Value None of type 'NoneType' does not support len().",
        how_to_fix="Provide a sized container or collection (e.g., list, dict, str, set).",
        exception=TypeError,
        verbose=False,
    )