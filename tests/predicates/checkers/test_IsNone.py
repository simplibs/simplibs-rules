"""Tests for the IsNone checker rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.checkers import IsNone


def test_is_none_contract(subtests):
    """Verify the complete contract of IsNone rule using master orchestrator."""
    rule = IsNone()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[None],
        invalid_values=[False, 0, "", [], True],
        rule_factory=IsNone,
        deep_check=True,
        verbose=False,
    )


def test_is_none_exception_details(subtests):
    """Verify exact exception details when passing a non-None value."""
    rule = IsNone()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("not none", Kwargs(value_name="config")),
        exception_type=ValidationError,
        label="config",
        value="not none",
        error_name="IS_NONE_ERROR",
        expected="None",
        problem="Value is not None (got 'not none').",
        how_to_fix="Provide None.",
        exception=ValueError,
        verbose=False,
    )