"""Tests for the IsSupersetOf collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections import IsSupersetOf


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_is_superset_of_contract(subtests):
    """Verify the complete contract of IsSupersetOf rule using master orchestrator."""
    rule = IsSupersetOf({"read", "write"})

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            ["read", "write"],
            ["read", "write", "execute"],
            {"read", "write", "admin"},
        ],
        invalid_values=[
            ["read"],
            ["write"],
            ["execute"],
            [],
            123,
            None,
        ],
        rule_factory=IsSupersetOf,
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

def test_is_superset_of_missing_elements_exception(subtests):
    """Verify diagnosis (ValueError) when required elements are missing from the collection."""
    rule = IsSupersetOf(["read", "write", "execute"])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(["read"], Kwargs(value_name="permissions")),
        exception_type=ValidationError,
        label="permissions",
        value=["read"],
        error_name="IS_SUPERSET_OF_ERROR",
        expected="superset of {'execute', 'read', 'write'}",
        problem="Value is missing required element(s): {'execute', 'write'}.",
        how_to_fix="Include element(s): {'execute', 'write'}.",
        exception=ValueError,
        verbose=False,
    )


def test_is_superset_of_non_iterable_exception(subtests):
    """Verify diagnosis (TypeError) when the object is not iterable."""
    rule = IsSupersetOf(["a", "b"])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(100, Kwargs(value_name="raw_val")),
        exception_type=ValidationError,
        label="raw_val",
        value=100,
        error_name="IS_SUPERSET_OF_ERROR",
        expected="superset of {'a', 'b'}",
        problem="Value 100 of type 'int' is not iterable.",
        how_to_fix="Provide an iterable container (e.g., list, tuple, set).",
        exception=TypeError,
        verbose=False,
    )


def test_is_superset_of_unhashable_elements_exception(subtests):
    """Verify diagnosis (ValueError) when the value contains unhashable elements."""
    rule = IsSupersetOf([1, 2])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([[1, 2]], Kwargs(value_name="nested")),
        exception_type=ValidationError,
        label="nested",
        value=[[1, 2]],
        error_name="IS_SUPERSET_OF_ERROR",
        expected="superset of {1, 2}",
        problem="Value [[1, 2]] contains unhashable elements that cannot be compared as a set.",
        how_to_fix="Ensure all elements in the container are hashable (e.g., strings, numbers, tuples).",
        exception=ValueError,
        verbose=False,
    )