"""Tests for the HasRemainder arithmetic rule."""

from typing import Any
import pytest

# Test tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.predicates.arithmetic import HasRemainder


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_has_remainder_contract(subtests):
    """Verify the complete contract of HasRemainder rule using master orchestrator."""
    rule = HasRemainder(divisor=3, remainder=1)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 4, 7, 10, -2, -5],
        invalid_values=[0, 2, 3, 5, 1.0, "1", None, True, False],
        rule_factory=HasRemainder,
        invalid_init_params=[
            ((0, 1), {}),         # Divisor 0 raises ParamError
            (("3", 1), {}),       # Non-integer divisor raises ParamError
            ((3, "1"), {}),       # Non-integer remainder raises ParamError
            ((3, -1), {}),        # Negative remainder raises ParamError
            ((3, 3), {}),         # Remainder equal to divisor raises ParamError
            ((3, 4), {}),         # Remainder greater than divisor raises ParamError
            ((3, True), {}),      # Bool remainder raises ParamError
        ],
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_has_remainder_unexpected_remainder_exception(subtests):
    """Verify diagnosis upon remainder failure for an integer (ValueError)."""
    rule = HasRemainder(divisor=5, remainder=2)

    # 14 % 5 == 4 (expected 2)
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(14, Kwargs(value_name="number")),
        exception_type=ValidationError,
        label="number",
        value=14,
        error_name="HAS_REMAINDER_ERROR",
        expected="remainder 2 when divided by 5",
        problem="Value 14 has remainder 4 when divided by 5, but expected 2.",
        how_to_fix="Provide an integer 'n' where n % 5 == 2 (e.g., 2, 7).",
        exception=ValueError,
        verbose=False,
    )


def test_has_remainder_type_error_exception(subtests):
    """Verify that passing a non-integer value raises an exception wrapped in TypeError."""
    rule = HasRemainder(divisor=3, remainder=1)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("4", Kwargs(value_name="input_val")),
        exception_type=ValidationError,
        label="input_val",
        value="4",
        error_name="HAS_REMAINDER_ERROR",
        expected="remainder 1 when divided by 3",
        problem="Value '4' of type 'str' is not an integer.",
        how_to_fix="Provide an integer value.",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. SPECIFIC EDGE CASES & FUNCTIONALITY
# ==============================================================================

def test_has_remainder_with_negative_divisor():
    """Verify functionality with negative divisor (remainder in constructor is positive, but Python modulo with negative divisor returns negative number)."""
    # For divisor=-5 Python yields e.g.:
    # -3 % -5 == -3
    # 2 % -5 == -3
    # 7 % -5 == -3
    # For n % -5 == 2, the value would need to return 2, which Python evaluates for n e.g.: -8 % -5 == -3, but -13 % -5 == -3.
    # In Python: (n % -d) is always <= 0.
    # If remainder=2 is provided for divisor=-5, no int in Python will satisfy it (since n % -5 yields values in range -4 to 0).

    # To verify negative divisor with valid positive remainder (if code logic requires it):
    rule = HasRemainder(divisor=-5, remainder=2)

    # Since Python value % negative_divisor is always negative or zero,
    # for any int, value % -5 returns a negative number, so remainder=2 will not be satisfied for any positive/negative number:
    assert rule.is_valid(7) is False   # 7 % -5 == -3 != 2
    assert rule.is_valid(-3) is False  # -3 % -5 == -3 != 2
    assert rule.is_valid(2) is False   # 2 % -5 == -3 != 2


def test_has_remainder_rejects_booleans():
    """Verify that True/False are strictly rejected."""
    rule = HasRemainder(divisor=2, remainder=1)

    assert rule.is_valid(True) is False
    assert rule.is_valid(False) is False