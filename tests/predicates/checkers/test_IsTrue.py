"""Tests for the IsTrue checker rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.checkers import IsTrue


def test_is_true_contract(subtests):
    """Verify the complete contract of IsTrue rule using master orchestrator."""
    rule = IsTrue()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[True],
        invalid_values=[False, 1, "True", [1], None],
        rule_factory=IsTrue,
        deep_check=True,
        verbose=False,
    )


def test_is_true_exception_details(subtests):
    """Verify exact exception details when passing a non-True value."""
    rule = IsTrue()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(1, Kwargs(value_name="is_active")),
        exception_type=ValidationError,
        label="is_active",
        value=1,
        error_name="IS_TRUE_ERROR",
        expected="True",
        problem="Value is not True (got 1).",
        how_to_fix="Provide the literal boolean value True.",
        exception=ValueError,
        verbose=False,
    )