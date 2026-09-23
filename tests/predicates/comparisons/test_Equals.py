"""Tests for the Equals equality rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.comparisons import Equals


def test_equals_contract(subtests):
    """Verify the contract of the Equals rule."""
    rule = Equals("active")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["active"],
        invalid_values=["inactive", "ACTIVE", 123, None, False, ["active"]],
        deep_check=True,
        verbose=False,
    )


def test_equals_exception(subtests):
    """Verify the exception card diagnosis upon value inequality."""
    rule = Equals("active")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("pending", Kwargs(value_name="status")),
        exception_type=ValidationError,
        label="status",
        value="pending",
        error_name="EQUALS_ERROR",
        expected="'active'",
        problem="Value 'pending' is not equal to expected 'active'.",
        how_to_fix="Provide a value equal to 'active'.",
        exception=ValueError,
    )