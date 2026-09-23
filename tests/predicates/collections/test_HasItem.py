"""Tests for the HasItem collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections import HasItem


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_has_item_contract(subtests):
    """Verify the complete contract of HasItem rule using master orchestrator."""
    rule = HasItem("admin")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            ["admin", "user"],
            ("admin",),
            {"admin", "editor"},
            {"admin": True, "guest": False},
            "administrator",
        ],
        invalid_values=[
            ["user", "guest"],
            (),
            {"guest": True},
            123,
            None,
        ],
        rule_factory=HasItem,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_has_item_missing_item_exception(subtests):
    """Verify diagnosis (ValueError) when container is missing the required item."""
    rule = HasItem("admin")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(["user", "guest"], Kwargs(value_name="roles")),
        exception_type=ValidationError,
        label="roles",
        value=["user", "guest"],
        error_name="HAS_ITEM_ERROR",
        expected="container with item 'admin'",
        problem="Value does not contain item 'admin'.",
        how_to_fix="Provide a container that includes item 'admin'.",
        exception=ValueError,
        verbose=False,
    )


def test_has_item_unsupported_membership_exception(subtests):
    """Verify diagnosis (TypeError) when object does not support the membership operator ('in')."""
    rule = HasItem("admin")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="user_id")),
        exception_type=ValidationError,
        label="user_id",
        value=123,
        error_name="HAS_ITEM_ERROR",
        expected="container with item 'admin'",
        problem="Value 123 of type 'int' does not support membership testing.",
        how_to_fix="Provide a container that supports the 'in' operator.",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. SPECIFIC EDGE CASES & CUSTOM CONTAINERS
# ==============================================================================

def test_has_item_with_complex_and_falsy_items():
    """Verify functionality for falsy or complex items (None, False, 0, tuples)."""
    rule_none = HasItem(None)
    assert rule_none.is_valid([1, None, 3]) is True
    assert rule_none.is_valid([1, 2, 3]) is False

    rule_false = HasItem(False)
    assert rule_false.is_valid([True, False]) is True
    assert rule_false.is_valid([True]) is False

    rule_tuple = HasItem((1, 2))
    assert rule_tuple.is_valid([(1, 2), (3, 4)]) is True


def test_has_item_custom_container_protocol():
    """Verify that a custom class implementing __contains__ works properly."""

    class CustomContainer:
        def __contains__(self, item: Any) -> bool:
            return item == "secret"

    rule = HasItem("secret")
    assert rule.is_valid(CustomContainer()) is True

    rule_missing = HasItem("other")
    assert rule_missing.is_valid(CustomContainer()) is False