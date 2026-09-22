"""Tests for the NotEquals equality rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.comparisons import NotEquals


def test_not_equals_contract(subtests):
    """Verify the contract of the NotEquals rule."""
    rule = NotEquals(0)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, -1, "0", None, [0]],
        invalid_values=[0, 0.0, False],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_not_equals_exception(subtests):
    """Verify exception card diagnosis upon forbidden match."""
    rule = NotEquals(0)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(0, Kwargs(value_name="divisor")),
        exception_type=ValidationError,
        label="divisor",
        value=0,
        error_name="NOT_EQUALS_ERROR",
        expected="value not equal to 0",
        problem="Value 0 is equal to forbidden value 0.",
        how_to_fix="Provide a value other than 0.",
        exception=ValueError,
    )