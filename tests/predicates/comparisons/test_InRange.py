"""Tests for the InRange comparison rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.comparisons import InRange


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_in_range_contract(subtests):
    """Verify the complete contract of InRange rule using master orchestrator."""
    rule = InRange(1, 10)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 5, 10, 1.0, 9.9],
        invalid_values=[0, 11, -5, "5", None, [1]],
        invalid_init_params=[
            ((10, 1), {}),         # Swapped bounds (min > max) raise ParamError
            ((1, "10"), {}),       # Incomparable bound types raise ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_in_range_out_of_bounds_exception(subtests):
    """Verify diagnosis (ValueError) when value lies outside defined range."""
    rule = InRange(10, 20, include_min=True, include_max=False)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(25, Kwargs(value_name="score")),
        exception_type=ValidationError,
        label="score",
        value=25,
        error_name="IN_RANGE_ERROR",
        expected="value in range 10 to 20",
        problem="Value 25 falls outside the expected range [10, 20).",
        how_to_fix="Provide a value within the range [10, 20).",
        exception=ValueError,
        verbose=False,
    )


def test_in_range_incomparable_type_exception(subtests):
    """Verify diagnosis (TypeError) when input type cannot be compared to bounds."""
    rule = InRange(1, 10)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("text", Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        value="text",
        error_name="IN_RANGE_ERROR",
        expected="value in range 1 to 10",
        problem="Cannot compare 'str' ('text') with range bounds 'int' (1) and 'int' (10).",
        how_to_fix="Provide a value of a type comparable with 'int'.",
        exception=TypeError,
    )


# ==============================================================================
# 3. SPECIFIC EDGE CASES & INCLUSIVITY
# ==============================================================================

def test_in_range_inclusivity_variations():
    """Verify all combinations of include_min and include_max."""
    # Exclusive on both ends: (5, 10)
    rule_exclusive = InRange(5, 10, include_min=False, include_max=False)
    assert rule_exclusive.is_valid(5) is False
    assert rule_exclusive.is_valid(10) is False
    assert rule_exclusive.is_valid(6) is True
    assert rule_exclusive.is_valid(9) is True

    # Inclusive min only: [5, 10)
    rule_min_only = InRange(5, 10, include_min=True, include_max=False)
    assert rule_min_only.is_valid(5) is True
    assert rule_min_only.is_valid(10) is False

    # Inclusive max only: (5, 10]
    rule_max_only = InRange(5, 10, include_min=False, include_max=True)
    assert rule_max_only.is_valid(5) is False
    assert rule_max_only.is_valid(10) is True