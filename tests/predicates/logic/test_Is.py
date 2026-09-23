"""Tests for the Is rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.logic import Is


SENTINEL = object()


def test_is_contract(subtests):
    """Verify the complete contract of the Is rule."""
    rule = Is(SENTINEL)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[SENTINEL],
        invalid_values=[object(), "SENTINEL", 123, None, []],
        deep_check=True,
        verbose=False,
    )


def test_is_exception(subtests):
    """Verify diagnosis (ValueError) when object does not share identity."""
    rule = Is(None)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("not_none", Kwargs(value_name="state")),
        exception_type=ValidationError,
        label="state",
        value="not_none",
        error_name="IS_ERROR",
        expected="value identical to None",
        problem="Value is not identical to None.",
        how_to_fix="Provide the exact object instance None.",
        exception=ValueError,
        verbose=False,
    )