"""Tests for the DivisibleBy arithmetic rule."""

from typing import Any
import pytest

# Test tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.predicates.arithmetic import DivisibleBy


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_divisible_by_contract(subtests):
    """Verify the complete contract of DivisibleBy rule using master orchestrator."""
    rule = DivisibleBy(3)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[3, 6, 9, 0, -3, -6],
        invalid_values=[1, 2, 4, 3.0, "3", None, True, False],
        rule_factory=DivisibleBy,
        invalid_init_params=[
            ((0,), {}),           # Divisor 0 raises ParamError
            (("3",), {}),         # Non-integer divisor raises ParamError
            ((3.0,), {}),         # Float divisor raises ParamError
            ((True,), {}),        # Bool divisor raises ParamError
            ((None,), {}),        # None divisor raises ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_divisible_by_not_divisible_exception(subtests):
    """Verify diagnosis upon divisibility failure for an integer (ValueError)."""
    rule = DivisibleBy(5)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(12, Kwargs(value_name="amount")),
        exception_type=ValidationError,
        label="amount",
        value=12,
        error_name="DIVISIBLE_BY_ERROR",
        expected="multiple of 5",
        problem="Value 12 is not divisible by 5.",
        how_to_fix="Provide a multiple of 5 (e.g., 5, 10).",
        exception=ValueError,
        verbose=False,
    )


def test_divisible_by_type_error_exception(subtests):
    """Verify that passing a non-integer value raises an exception wrapped in TypeError."""
    rule = DivisibleBy(2)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("4", Kwargs(value_name="code")),
        exception_type=ValidationError,
        label="code",
        value="4",
        error_name="DIVISIBLE_BY_ERROR",
        expected="multiple of 2",
        problem="Value '4' of type 'str' is not an integer.",
        how_to_fix="Provide an integer value.",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. SPECIFIC EDGE CASES & FUNCTIONALITY
# ==============================================================================

def test_divisible_by_negative_divisor_and_values():
    """Verify divisibility functionality with a negative divisor and negative values."""
    rule = DivisibleBy(-4)

    assert rule.is_valid(8) is True
    assert rule.is_valid(-12) is True
    assert rule.is_valid(0) is True
    assert rule.is_valid(5) is False


def test_divisible_by_rejects_booleans():
    """Verify that True/False are strictly rejected even though they inherit from int in Python."""
    rule = DivisibleBy(1)

    assert rule.is_valid(True) is False
    assert rule.is_valid(False) is False