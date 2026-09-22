"""Tests for the IsSubsetOf collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections import IsSubsetOf


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_is_subset_of_contract(subtests):
    """Verify the complete contract of IsSubsetOf rule using master orchestrator."""
    rule = IsSubsetOf({"admin", "editor", "viewer"})

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            ["admin"],
            ["admin", "editor"],
            ("viewer",),
            set(),
            [],
        ],
        invalid_values=[
            ["admin", "superuser"],
            ["guest"],
            123,
            None,
        ],
        rule_factory=IsSubsetOf,
        invalid_init_params=[
            ((123,), {}),       # Non-container reference parameter raises ParamError
            (("string",), {}),   # String reference raises ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_is_subset_of_extra_elements_exception(subtests):
    """Verify diagnosis (ValueError) when the collection contains elements outside reference."""
    rule = IsSubsetOf([1, 2, 3, 4, 5])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([1, 2, 99], Kwargs(value_name="selected_ids")),
        exception_type=ValidationError,
        label="selected_ids",
        value=[1, 2, 99],
        error_name="IS_SUBSET_OF_ERROR",
        expected="subset of {1, 2, 3, 4, 5}",
        problem="Value contains element(s) not in reference: {99}.",
        how_to_fix="Remove element(s) not in {1, 2, 3, 4, 5}: {99}.",
        exception=ValueError,
        verbose=False,
    )


def test_is_subset_of_non_iterable_exception(subtests):
    """Verify diagnosis (TypeError) when the object is not iterable."""
    rule = IsSubsetOf(["a", "b", "c"])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(50, Kwargs(value_name="input_val")),
        exception_type=ValidationError,
        label="input_val",
        value=50,
        error_name="IS_SUBSET_OF_ERROR",
        expected="subset of {'a', 'b', 'c'}",
        problem="Value 50 of type 'int' is not iterable.",
        how_to_fix="Provide an iterable container (e.g., list, tuple, set).",
        exception=TypeError,
        verbose=False,
    )


def test_is_subset_of_unhashable_elements_exception(subtests):
    """Verify diagnosis (ValueError) when the value contains unhashable elements."""
    rule = IsSubsetOf([1, 2, 3])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([[1, 2]], Kwargs(value_name="nested_lists")),
        exception_type=ValidationError,
        label="nested_lists",
        value=[[1, 2]],
        error_name="IS_SUBSET_OF_ERROR",
        expected="subset of {1, 2, 3}",
        problem="Value [[1, 2]] contains unhashable elements that cannot be compared as a set.",
        how_to_fix="Ensure all elements in the container are hashable (e.g., strings, numbers, tuples).",
        exception=ValueError,
        verbose=False,
    )