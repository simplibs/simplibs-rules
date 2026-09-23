"""Tests for the AllOf container rule."""

from typing import Any
import pytest

# Testing tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.containers import AllOf
from simplibs.rules.predicates.numeric import IsInteger
from simplibs.rules.predicates.comparisons import GreaterThan, LessThan


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_all_of_contract(subtests):
    """Verify the complete contract of AllOf using the master orchestrator."""
    rule = AllOf(IsInteger(), GreaterThan(0))

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 10, 100],               # Must satisfy both rules
        invalid_values=[-5, 0, "string", None],  # Fails at least one of the rules
        rule_factory=AllOf,
        invalid_init_params=[
            ((), {}),  # AllOf() with no arguments raises ParamError
        ],
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST (Delegated exception from child rule)
# ==============================================================================

def test_all_of_delegates_child_exception_details(subtests):
    """Verify that AllOf transparently adopts the diagnostic card of the first failing rule."""
    rule = AllOf(IsInteger(), GreaterThan(0))

    # Test 1: Fails immediately on the first rule (IsInteger) for string "abc"
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("abc", Kwargs(value_name="age")),
        exception_type=ValidationError,
        label="age",
        expected="an integer",
        problem="is not an integer",
        verbose=False,
    )

    # Test 2: Passes IsInteger, but fails on GreaterThan(0) for number -5
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(-5, Kwargs(value_name="score")),
        exception_type=ValidationError,
        label="score",
        expected="greater than 0",
        verbose=False,
    )


# ==============================================================================
# 3. SELF-FLATTENING CONSTRUCTOR & OPERATOR CHAINING
# ==============================================================================

def test_all_of_self_flattening(subtests):
    """Verify that AllOf automatically flattens nested AllOf instances into a single flat structure."""
    r1, r2, r3 = IsInteger(), GreaterThan(0), LessThan(100)

    with subtests.test("manual_nested_instantiation"):
        # AllOf(AllOf(r1, r2), r3) -> should create flat AllOf(r1, r2, r3)
        rule = AllOf(AllOf(r1, r2), r3)
        assert len(rule.rules) == 3
        assert rule.rules == (r1, r2, r3)

    with subtests.test("operator_and_chaining"):
        # r1 & r2 & r3 -> evaluates as (r1 & r2) & r3
        rule = r1 & r2 & r3
        assert isinstance(rule, AllOf)
        assert len(rule.rules) == 3
        assert rule.rules == (r1, r2, r3)


# ==============================================================================
# 4. EDGE CASES & SHORT-CIRCUIT EVALUATION
# ==============================================================================

def test_all_of_short_circuit_eval():
    """Verify that AllOf evaluates rules left-to-right and stops on the first failure."""
    call_log = []

    def rule_1(val):
        call_log.append("rule_1")
        return False

    def rule_2(val):
        call_log.append("rule_2")
        return True

    rule = AllOf(rule_1, rule_2)
    assert rule.is_valid(10) is False
    assert call_log == ["rule_1"]