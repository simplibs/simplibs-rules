"""Tests for the NoneOf container rule."""

from typing import Any
import pytest

# Testing tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.containers import AllOf, AnyOf, NoneOf
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
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST
# ==============================================================================

def test_none_of_single_matched_rule_exception(subtests):
    """Verify detailed exception structure when a value violates exactly one rule."""
    # Expected texts are built from describe(), so the test stays valid
    # whenever a predicate changes its description.
    zero, none = IsZero(), IsNone()
    rule = NoneOf(zero, none)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(0, Kwargs(value_name="status_code")),
        exception_type=ValidationError,
        label="status_code",
        value=0,
        error_name="NONE_OF_ERROR",
        expected=f"value satisfying none of: {zero.describe()}, {none.describe()}",
        problem=f"Value unexpectedly satisfied forbidden rule(s): {zero.describe()}.",
        how_to_fix=f"Modify the value so that it does not match any of: {zero.describe()}, {none.describe()}.",
        exception=ValueError,
        verbose=False,
    )


def test_none_of_multiple_matched_rules_exception(subtests):
    """Verify detailed exception structure when a value violates multiple rules simultaneously."""
    # 0 is both IsZero and IsInteger
    zero, integer = IsZero(), IsInteger()
    rule = NoneOf(zero, integer)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(0, Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        value=0,
        error_name="NONE_OF_ERROR",
        expected=f"value satisfying none of: {zero.describe()}, {integer.describe()}",
        problem=f"Value unexpectedly satisfied forbidden rule(s): {zero.describe()}, {integer.describe()}.",
        how_to_fix=f"Modify the value so that it does not match any of: {zero.describe()}, {integer.describe()}.",
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


# ==============================================================================
# 4. DESCRIPTION TEST
# ==============================================================================

def is_a(value: Any) -> bool:
    return True


def is_b(value: Any) -> bool:
    return True


def is_c(value: Any) -> bool:
    return True


def test_none_of_describe(subtests):
    """Verify that NoneOf lists its operands inside 'none of (...)'."""

    with subtests.test("simple operands"):
        assert NoneOf(is_a, is_b).describe() == "none of (is_a, is_b)"

    with subtests.test("AnyOf operand needs no parentheses"):
        assert NoneOf(AnyOf(is_a, is_b), is_c).describe() == "none of (is_a | is_b, is_c)"

    with subtests.test("AllOf operand needs no parentheses"):
        assert NoneOf(AllOf(is_a, is_b), is_c).describe() == "none of (is_a & is_b, is_c)"
