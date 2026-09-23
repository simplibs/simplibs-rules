"""Tests for the HasLength rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import HasLength


# ==============================================================================
# 1. CONTRACT TESTS (Master Contracts)
# ==============================================================================

def test_has_length_exact_contract(subtests):
    """Verify the complete contract of HasLength rule for exact length."""
    rule = HasLength(length=3)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["abc", [1, 2, 3], (1, 2, 3), {"a": 1, "b": 2, "c": 3}],
        invalid_values=["ab", "abcd", [], 123, None],
        invalid_init_params=[
            ((), {}),                               # No parameters -> ParamError
            ((3,), {"min_length": 1}),             # Conflict length + min_length -> ParamError
            ((-1,), {}),                            # Negative length -> ParamError
            (("3",), {}),                           # String length -> ParamError
        ],
        deep_check=True,
        verbose=False,
    )


def test_has_length_range_contract(subtests):
    """Verify the complete contract of HasLength rule for length range."""
    rule = HasLength(min_length=2, max_length=4)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["ab", "abc", "abcd", [1, 2], [1, 2, 3, 4]],
        invalid_values=["a", "abcde", "", 456, None],
        invalid_init_params=[
            ((), {"min_length": 5, "max_length": 2}),  # Swapped bounds (min > max) -> ParamError
            ((), {"min_length": -1}),                  # Negative min_length -> ParamError
            ((), {"max_length": 1.5}),                 # Non-integer max_length -> ParamError
        ],
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TESTS
# ==============================================================================

def test_has_length_value_out_of_bounds_exception(subtests):
    """Verify diagnosis (ValueError) when value has invalid length."""
    rule = HasLength(min_length=3, max_length=5)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("hi", Kwargs(value_name="username")),
        exception_type=ValidationError,
        label="username",
        value="hi",
        error_name="HAS_LENGTH_ERROR",
        expected="length between 3 and 5",
        problem="Value has length 2, expected length between 3 and 5.",
        how_to_fix="Provide a value with length between 3 and 5.",
        exception=ValueError,
        verbose=False,
    )


def test_has_length_non_sized_type_exception(subtests):
    """Verify diagnosis (TypeError) when passed object lacks len()."""
    rule = HasLength(length=10)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(12345, Kwargs(value_name="user_id")),
        exception_type=ValidationError,
        label="user_id",
        value=12345,
        error_name="HAS_LENGTH_ERROR",
        expected="length 10",
        problem="Value 12345 of type 'int' has no len().",
        how_to_fix="Provide a sized collection (e.g. list, str, tuple) with length 10.",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. SPECIFIC BOUNDARY VARIATIONS (min_length / max_length standalone)
# ==============================================================================

def test_has_length_boundary_variations():
    """Verify behavior when using min_length only or max_length only."""
    # min_length only
    rule_min = HasLength(min_length=2)
    assert rule_min.is_valid("a") is False
    assert rule_min.is_valid("ab") is True
    assert rule_min.is_valid("abc") is True

    # max_length only
    rule_max = HasLength(max_length=2)
    assert rule_max.is_valid("") is True
    assert rule_max.is_valid("ab") is True
    assert rule_max.is_valid("abc") is False