"""Tests for the Not container rule."""

from typing import Any
import pytest

# Testing tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.containers import Not
from simplibs.rules.predicates.numeric import IsZero
from simplibs.rules.predicates.strings import IsString
from simplibs.rules.predicates.checkers import IsNone


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_not_contract(subtests):
    """Verify the complete contract of Not using the master orchestrator."""
    rule = Not(IsNone())

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[42, "hello", [1, 2], False],
        invalid_values=[None],
        rule_factory=Not,
        invalid_init_params=[
            ((123,), {}),       # Non-callable parameter raises ParamError
            (("string",), {}),  # Non-callable parameter raises ParamError
            ((None,), {}),      # None instead of rule raises ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST
# ==============================================================================

def test_not_exception_details(subtests):
    """Verify exact diagnostic card details when a value satisfies the forbidden rule."""
    rule = Not(IsZero())

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(0, Kwargs(value_name="counter")),
        exception_type=ValidationError,
        label="counter",
        value=0,
        error_name="NOT_RULE_ERROR",
        expected="value NOT satisfying IsZero",
        problem="Value unexpectedly satisfied forbidden rule/condition: IsZero.",
        how_to_fix="Provide a value that does not satisfy IsZero.",
        exception=ValueError,
        verbose=False,
    )


# ==============================================================================
# 3. EDGE CASES & FUNCTIONALITY
# ==============================================================================

def test_not_valid_cases():
    """Verify that is_valid returns True for values that do not satisfy the nested rule."""
    rule = Not(IsString())

    assert rule.is_valid(123) is True
    assert rule.is_valid(True) is True
    assert rule.is_valid("test") is False


def test_not_with_custom_predicate():
    """Verify that Not works correctly with a plain lambda predicate."""
    rule = Not(lambda x: x > 10)

    assert rule.is_valid(5) is True
    assert rule.is_valid(10) is True
    assert rule.is_valid(15) is False