"""Tests for the IsNot rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.logic import IsNot


FORBIDDEN = object()


def test_is_not_contract(subtests):
    """Verify the complete contract of the IsNot rule."""
    rule = IsNot(FORBIDDEN)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[object(), "FORBIDDEN", 123, None, []],
        invalid_values=[FORBIDDEN],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_not_exception(subtests):
    """Verify diagnosis (ValueError) when forbidden object is passed."""
    rule = IsNot(None)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(None, Kwargs(value_name="token")),
        exception_type=ValidationError,
        label="token",
        value=None,
        error_name="IS_NOT_ERROR",
        expected="value not identical to None",
        problem="Value is identical to forbidden object None.",
        how_to_fix="Provide any object reference other than None.",
        exception=ValueError,
        verbose=False,
    )