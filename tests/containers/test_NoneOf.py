"""Tests for the NoneOf container rule."""

from typing import Any
import pytest

# Testing tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.containers import NoneOf
from simplibs.rules.predicates.numeric import IsInteger, IsZero
from simplibs.rules.predicates.strings import IsString
from simplibs.rules.predicates.checkers import IsNone


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_none_of_contract(subtests):
    """Verify the complete contract of NoneOf using the master orchestrator."""
    rule = NoneOf(IsInteger(), IsString())

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[None, 3.14, True, [1, 2, 3]],
        invalid_values=[42, "hello"],
        rule_factory=NoneOf,
        invalid_init_params=[
            ((), {}),  # NoneOf() with no arguments raises ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST
# ==============================================================================

def test_none_of_single_matched_rule_exception(subtests):
    """Verify detailed exception structure when a value violates exactly one rule."""
    rule = NoneOf(IsZero(), IsNone())

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(0, Kwargs(value_name="status_code")),
        exception_type=ValidationError,
        label="status_code",
        value=0,
        error_name="NONE_OF_ERROR",
        expected="value satisfying none of: IsZero, IsNone",
        problem="Value unexpectedly satisfied forbidden rule(s): IsZero.",
        how_to_fix="Modify the value so that it does not match any of: IsZero, IsNone.",
        exception=ValueError,
        verbose=False,
    )


def test_none_of_multiple_matched_rules_exception(subtests):
    """Verify detailed exception structure when a value violates multiple rules simultaneously."""
    # 0 is both IsZero and IsInteger
    rule = NoneOf(IsZero(), IsInteger())

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(0, Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        value=0,
        error_name="NONE_OF_ERROR",
        expected="value satisfying none of: IsZero, IsInteger",
        problem="Value unexpectedly satisfied forbidden rule(s): IsZero, IsInteger.",
        how_to_fix="Modify the value so that it does not match any of: IsZero, IsInteger.",
        exception=ValueError,
        verbose=False,
    )


# ==============================================================================
# 3. EDGE CASES & FUNCTIONALITY
# ==============================================================================

def test_none_of_valid_cases():
    """Verify that is_valid returns True if the value satisfies none of the rules."""
    rule = NoneOf(IsZero(), IsNone())

    assert rule.is_valid(42) is True
    assert rule.is_valid("test") is True
    assert rule.is_valid(1) is True


def test_none_of_with_custom_predicates():
    """Verify that NoneOf works correctly with standard callable/lambda predicates."""
    rule = NoneOf(lambda x: x > 10, lambda x: x < 0)

    assert rule.is_valid(5) is True
    assert rule.is_valid(10) is True
    assert rule.is_valid(15) is False
    assert rule.is_valid(-2) is False