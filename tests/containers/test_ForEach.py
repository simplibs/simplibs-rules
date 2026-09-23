"""Tests for the ForEach container rule."""

from typing import Any
import pytest

# Testing tools
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.containers import ForEach
from simplibs.rules.predicates.numeric import IsInteger
from simplibs.rules.predicates.comparisons import GreaterThan


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_for_each_contract(subtests):
    """Verify the complete contract of ForEach using the master orchestrator."""
    # All elements in collections must be integers > 0
    rule = ForEach(GreaterThan(0))

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            [1, 2, 3],
            (10, 20),
            {5},
            range(1, 5),
            [],  # Empty collection is trivially valid (all() returns True)
        ],
        invalid_values=[
            [1, -2, 3],      # Second element violates rule (<= 0)
            [1, "text", 3],  # Second element violates comparison
            123,             # Non-iterable value
            None,            # Non-iterable value
        ],
        rule_factory=ForEach,
        invalid_init_params=[
            (("not_callable",), {}),  # Non-callable rule raises ParamError
            ((None,), {}),            # None instead of rule raises ParamError
        ],
        deep_check=True,
        check_value=False,  # ForEach delegates to collection elements -> exc.value is failed item, not whole collection
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST & INDEXING
# ==============================================================================

def test_for_each_delegates_to_child_exception_with_index(subtests):
    """Verify that ForEach propagates exception from failed item with proper index in label."""
    rule = ForEach(IsInteger())

    # Element at index 2 ("bad") fails on IsInteger
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([10, 20, "bad", 40], Kwargs(value_name="items")),
        exception_type=ValidationError,
        label="items[2]",
        value="bad",
        expected="integer",
        verbose=False,
    )


def test_for_each_non_iterable_value_delegates_to_is_iterable(subtests):
    """Verify that non-iterable values delegate exception construction to IsIterable()."""
    rule = ForEach(IsInteger())

    # Number 123 is non-iterable -> fails on IsIterable contract
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="payload")),
        exception_type=ValidationError,
        label="payload",
        value=123,
        error_name="IS_ITERABLE_ERROR",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. EDGE CASES & BEHAVIOR
# ==============================================================================

def test_for_each_with_plain_callable_predicate():
    """Verify functionality with a plain function / lambda expression instead of a Rule instance."""
    rule = ForEach(lambda x: isinstance(x, str) and x.startswith("a"))

    assert rule.is_valid(["apple", "avocado"]) is True
    assert rule.is_valid(["apple", "banana"]) is False


def test_for_each_unreachable_fallback():
    """Verify fallback exception (FOR_EACH_UNREACHABLE_ERROR) when build_exception is called directly unexpectedly."""
    rule = ForEach(IsInteger())

    # Manually calling build_exception with a valid collection where no item fails:
    exc = rule.build_exception([1, 2, 3], value_name="valid_list")

    assert isinstance(exc, ValidationError)
    assert exc.error_name == "FOR_EACH_UNREACHABLE_ERROR"
    assert exc.exception is RuntimeError