"""Tests for the IsInfinity rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsInfinity


def test_is_infinity_contract(subtests):
    """Verify the complete contract of the IsInfinity rule."""
    rule = IsInfinity()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[float("inf"), float("-inf")],
        # float("nan") excluded because NaN == NaN evaluates to False in Python
        invalid_values=[0.0, 10.5, 100, "inf", True, None],
        deep_check=True,
        verbose=False,
    )


def test_is_infinity_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input is not a float."""
    rule = IsInfinity()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("inf", Kwargs(value_name="bound")),
        exception_type=ValidationError,
        label="bound",
        value="inf",
        error_name="IS_INFINITY_ERROR",
        expected="float('inf') or float('-inf')",
        problem="Value 'inf' is of type 'str', expected float.",
        how_to_fix="Provide a float representing infinity, e.g. float('inf') or float('-inf').",
        exception=TypeError,
        verbose=False,
    )


def test_is_infinity_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when input is a finite float."""
    rule = IsInfinity()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(12.34, Kwargs(value_name="limit")),
        exception_type=ValidationError,
        label="limit",
        value=12.34,
        error_name="IS_INFINITY_ERROR",
        expected="float('inf') or float('-inf')",
        problem="Value 12.34 is a finite float.",
        how_to_fix="Provide float('inf') or float('-inf').",
        exception=ValueError,
        verbose=False,
    )