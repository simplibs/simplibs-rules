"""Tests for the IsContainer collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections.IsContainer import IsContainer, is_container


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_is_container_contract(subtests):
    """Verify the complete contract of IsContainer rule using master orchestrator."""
    rule = IsContainer()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            [1, 2, 3],
            ("a", "b"),
            {10, 20},
            frozenset([1, 2]),
            {"key": "value"},
            [],
            {},
        ],
        invalid_values=[
            "string",
            b"bytes",
            123,
            3.14,
            True,
            None,
        ],
        rule_factory=IsContainer,
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_is_container_exception_details(subtests):
    """Verify exact exception details (TypeError) when passing a non-container input."""
    rule = IsContainer()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("text_value", Kwargs(value_name="payload")),
        exception_type=ValidationError,
        label="payload",
        value="text_value",
        error_name="IS_CONTAINER_ERROR",
        expected="a container collection (list, tuple, set, dict)",
        problem="Value 'text_value' of type 'str' is not a container.",
        how_to_fix="Provide a valid container collection.",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. HELPER FUNCTION & CUSTOM CONTAINERS
# ==============================================================================

def test_is_container_helper_function():
    """Verify proper operation of the exported helper function is_container."""
    assert is_container([1, 2]) is True
    assert is_container({"a": 1}) is True
    assert is_container("text") is False
    assert is_container(123) is False


def test_is_container_custom_protocol():
    """Verify that a custom class implementing the Container protocol passes."""

    class CustomContainer:
        def __contains__(self, item: Any) -> bool:
            return True

    assert is_container(CustomContainer()) is True