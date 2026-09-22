"""Tests for the IsFalse checker rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.checkers import IsFalse


def test_is_false_contract(subtests):
    """Verify the complete contract of IsFalse rule using master orchestrator."""
    rule = IsFalse()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[False],
        invalid_values=[True, 0, "", [], None],
        rule_factory=IsFalse,
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_false_exception_details(subtests):
    """Verify exact exception details when passing a non-False value."""
    rule = IsFalse()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(True, Kwargs(value_name="flag")),
        exception_type=ValidationError,
        label="flag",
        value=True,
        error_name="IS_FALSE_ERROR",
        expected="False",
        problem="Value is not False (got True).",
        how_to_fix="Provide the literal boolean value False.",
        exception=ValueError,
        verbose=False,
    )