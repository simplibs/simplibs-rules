"""Tests for the AllUnique collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections import AllUnique


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_all_unique_contract(subtests):
    """Verify the complete contract of AllUnique rule using master orchestrator."""
    rule = AllUnique()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            [1, 2, 3],
            ("a", "b", "c"),
            {10, 20, 30},
            [],
            "abc",
        ],
        invalid_values=[
            [1, 2, 2, 3],
            ("a", "a", "b"),
            "aba",
            123,
            None,
        ],
        rule_factory=AllUnique,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_all_unique_duplicates_exception(subtests):
    """Verify diagnosis (ValueError) when the collection contains duplicate items."""
    rule = AllUnique()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([1, 2, 2, 3, 1], Kwargs(value_name="numbers")),
        exception_type=ValidationError,
        label="numbers",
        value=[1, 2, 2, 3, 1],
        error_name="ALL_UNIQUE_ERROR",
        expected="all-unique items",
        problem="Value contains duplicate item(s): [2, 1].",
        how_to_fix="Remove duplicate item(s): [2, 1].",
        exception=ValueError,
        verbose=False,
    )


def test_all_unique_non_iterable_exception(subtests):
    """Verify diagnosis (TypeError) when the object is not iterable."""
    rule = AllUnique()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(42, Kwargs(value_name="payload")),
        exception_type=ValidationError,
        label="payload",
        value=42,
        error_name="ALL_UNIQUE_ERROR",
        expected="all-unique items",
        problem="Value 42 of type 'int' is not iterable.",
        how_to_fix="Provide an iterable container (e.g., list, tuple, set).",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. SPECIFIC EDGE CASES & UNHASHABLE TYPES
# ==============================================================================

def test_all_unique_unhashable_items():
    """Verify fallback behavior for unhashable objects (e.g., lists within a list)."""
    rule = AllUnique()

    # Unique lists
    assert rule.is_valid([[1, 2], [3, 4]]) is True

    # Duplicate unhashable lists
    assert rule.is_valid([[1, 2], [1, 2]]) is False