"""Tests for the HasKey collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections import HasKey


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_has_key_contract(subtests):
    """Verify the complete contract of HasKey rule using master orchestrator."""
    rule = HasKey("id")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            {"id": 123, "name": "Alice"},
            {"id": None},
            ["id", "other"],
            "identity",
        ],
        invalid_values=[
            {"username": "bob"},
            {},
            ["name", "other"],
            123,
            None,
        ],
        rule_factory=HasKey,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_has_key_missing_key_exception(subtests):
    """Verify diagnosis (KeyError) when dictionary/collection is missing the required key."""
    rule = HasKey("email")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=({"username": "john_doe"}, Kwargs(value_name="user")),
        exception_type=ValidationError,
        label="user",
        value={"username": "john_doe"},
        error_name="HAS_KEY_ERROR",
        expected="mapping with key 'email'",
        problem="Value does not have key 'email'.",
        how_to_fix="Provide a mapping containing key 'email'.",
        exception=KeyError,
        verbose=False,
    )


def test_has_key_unsupported_lookup_exception(subtests):
    """Verify diagnosis (TypeError) when object does not support the membership operator ('in')."""
    rule = HasKey("id")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(100, Kwargs(value_name="data")),
        exception_type=ValidationError,
        label="data",
        value=100,
        error_name="HAS_KEY_ERROR",
        expected="mapping with key 'id'",
        problem="Value 100 of type 'int' does not support key lookup.",
        how_to_fix="Provide a mapping or container that supports the 'in' operator.",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. SPECIFIC EDGE CASES & NORMAL CLUSTERING
# ==============================================================================

def test_has_key_with_non_string_keys():
    """Verify functionality for non-string keys (int, tuple, etc.)."""
    rule_int = HasKey(42)
    assert rule_int.is_valid({42: "answer"}) is True
    assert rule_int.is_valid({1: "one"}) is False

    rule_tuple = HasKey((1, 2))
    assert rule_tuple.is_valid({(1, 2): "coordinates"}) is True