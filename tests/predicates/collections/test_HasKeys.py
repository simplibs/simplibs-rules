"""Tests for the HasKeys collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections import HasKeys


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_has_keys_contract(subtests):
    """Verify the complete contract of HasKeys rule using master orchestrator."""
    rule = HasKeys("id", "name")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob"},
        ],
        invalid_values=[
            {"id": 1},
            {"name": "Alice"},
            {},
            123,
            None,
        ],
        rule_factory=HasKeys,
        invalid_init_params=[
            ((), {}),  # No arguments raises ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_has_keys_missing_keys_exception(subtests):
    """Verify diagnosis (KeyError) when dictionary/collection is missing required keys."""
    rule = HasKeys("id", "role", "email")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=({"id": 10}, Kwargs(value_name="user_data")),
        exception_type=ValidationError,
        label="user_data",
        value={"id": 10},
        error_name="HAS_KEYS_ERROR",
        expected="mapping with keys ('id', 'role', 'email')",
        problem="Value is missing key(s): ['role', 'email'].",
        how_to_fix="Provide a mapping containing key(s): ['role', 'email'].",
        exception=KeyError,
        verbose=False,
    )


def test_has_keys_unsupported_lookup_exception(subtests):
    """Verify diagnosis (TypeError) when object does not support key lookup."""
    rule = HasKeys("a", "b")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(3.14, Kwargs(value_name="pi")),
        exception_type=ValidationError,
        label="pi",
        value=3.14,
        error_name="HAS_KEYS_ERROR",
        expected="mapping with keys ('a', 'b')",
        problem="Value 3.14 of type 'float' does not support key lookup.",
        how_to_fix="Provide a mapping or container that supports the 'in' operator.",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. SPECIFIC EDGE CASES & PARAMETER COUNT
# ==============================================================================

def test_has_keys_single_and_multiple_arguments():
    """Verify functionality when passing single or multiple keys of various types."""
    rule_single = HasKeys("single")
    assert rule_single.is_valid({"single": True}) is True
    assert rule_single.is_valid({"other": True}) is False

    rule_mixed = HasKeys("id", 42, (1, 2))
    assert rule_mixed.is_valid({"id": "ok", 42: "number", (1, 2): "tuple"}) is True
    assert rule_mixed.is_valid({"id": "ok", 42: "number"}) is False