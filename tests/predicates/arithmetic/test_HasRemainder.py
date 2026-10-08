"""Tests for the HasRemainder arithmetic rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.arithmetic import HasRemainder


def test_has_remainder_contract(subtests):
    """Verify the complete contract of HasRemainder rule using master orchestrator."""
    rule = HasRemainder(divisor=3, remainder=1)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 4, 7, 10, -2, -5],
        invalid_values=[0, 2, 3, 5, 1.0, "1", None, True, False],
        expected_description="remainder 1 when divided by 3",
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


def test_has_remainder_unexpected_remainder_exception(subtests):
    """Verify diagnosis upon remainder failure for an integer (ValueError)."""
    rule = HasRemainder(divisor=5, remainder=2)

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


def test_has_remainder_with_negative_divisor():
    """Verify functionality with negative divisor."""
    rule = HasRemainder(divisor=-5, remainder=2)

    assert rule.is_valid(7) is False
    assert rule.is_valid(-3) is False
    assert rule.is_valid(2) is False


def test_has_remainder_rejects_booleans():
    """Verify that True/False are strictly rejected."""
    rule = HasRemainder(divisor=2, remainder=1)

    assert rule.is_valid(True) is False
    assert rule.is_valid(False) is False


def test_has_remainder_describe():
    """Verify the description phrase built from divisor and remainder parameters."""
    assert HasRemainder(3, 1).describe() == "remainder 1 when divided by 3"
    assert HasRemainder(5, 2).describe() == "remainder 2 when divided by 5"