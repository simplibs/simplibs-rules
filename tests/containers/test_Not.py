"""Tests for the Not container rule."""

from typing import Any
import pytest

# Testing tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.containers import AllOf, AnyOf, Compose, Not
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
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST
# ==============================================================================

def test_not_exception_details(subtests):
    """Verify exact diagnostic card details when a value satisfies the forbidden rule."""
    # Expected texts are built from describe(), so the test stays valid
    # whenever a predicate changes its description.
    zero = IsZero()
    rule = Not(zero)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(0, Kwargs(value_name="counter")),
        exception_type=ValidationError,
        label="counter",
        value=0,
        error_name="NOT_RULE_ERROR",
        expected=f"value NOT satisfying {zero.describe()}",
        problem=f"Value unexpectedly satisfied forbidden rule/condition: {zero.describe()}.",
        how_to_fix=f"Provide a value that does not satisfy {zero.describe()}.",
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


# ==============================================================================
# 4. DESCRIPTION TEST
# ==============================================================================

def is_a(value: Any) -> bool:
    return True


def is_b(value: Any) -> bool:
    return True


def test_not_describe(subtests):
    """Verify that Not describes itself as 'not <rule>', parenthesizing compound operands."""

    with subtests.test("simple operand"):
        assert Not(is_a).describe() == "not is_a"

    with subtests.test("AnyOf operand is parenthesized"):
        assert Not(AnyOf(is_a, is_b)).describe() == "not (is_a | is_b)"

    with subtests.test("AllOf operand is parenthesized"):
        assert Not(AllOf(is_a, is_b)).describe() == "not (is_a & is_b)"

    with subtests.test("Compose operand is parenthesized"):
        assert Not(Compose(str.strip, is_a)).describe() == "not (after strip: is_a)"
