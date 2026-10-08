"""Tests for the Described container rule."""

from typing import Any
import pytest

# Testing tools
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.containers import AllOf, AnyOf, Described
from simplibs.rules.predicates.numeric import IsInteger


def is_a(value: Any) -> bool:
    return True


def is_b(value: Any) -> bool:
    return True


def is_c(value: Any) -> bool:
    return True


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_described_contract(subtests):
    """Verify the complete contract of Described using the master orchestrator."""
    rule = Described(IsInteger(), "whole number")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, -5, 0],
        invalid_values=["1", 1.5, None],
        expected_description="whole number",
        rule_factory=Described,
        invalid_init_params=[
            ((5, "text"), {}),             # Non-callable rule raises ParamError
            (("not_callable", "text"), {}),  # Non-callable rule raises ParamError
            ((None, "text"), {}),          # None instead of rule raises ParamError
        ],
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DELEGATION TESTS
# ==============================================================================

def test_described_describe_returns_fixed_text(subtests):
    """Verify that describe() returns the given text instead of the wrapped rule's own."""

    with subtests.test("wrapped Rule"):
        assert Described(IsInteger(), "whole number").describe() == "whole number"

    with subtests.test("wrapped plain callable"):
        assert Described(is_a, "something").describe() == "something"


def test_described_is_valid_delegates_to_wrapped_rule(subtests):
    """Verify that evaluation is identical to the wrapped rule or callable."""

    with subtests.test("wrapped Rule"):
        rule = Described(IsInteger(), "whole number")
        assert rule.is_valid(5) is True
        assert rule.is_valid("5") is False

    with subtests.test("wrapped plain callable"):
        rule = Described(lambda v: v > 0, "positive")
        assert rule.is_valid(5) is True
        assert rule.is_valid(-5) is False


def test_described_build_exception_delegates_to_wrapped_rule(subtests):
    """Verify that the failure card is the wrapped rule's own card."""
    inner = IsInteger()
    outer = Described(inner, "whole number")

    expected_card = inner.build_exception("abc", "age", "ctx")
    actual_card = outer.build_exception("abc", "age", "ctx")

    with subtests.test("type"):
        assert isinstance(actual_card, ValidationError)
        assert type(actual_card) is type(expected_card)

    with subtests.test("fields"):
        assert actual_card.error_name == expected_card.error_name
        assert actual_card.expected == expected_card.expected
        assert actual_card.problem == expected_card.problem
        assert actual_card.label == "age"
        assert actual_card.context == "ctx"
        assert actual_card.value == "abc"


def test_described_build_exception_for_plain_callable():
    """Verify that a wrapped plain callable gets the shared fallback card."""
    rule = Described(lambda v: v > 0, "positive")

    exc = rule.build_exception(-5, "num", "ctx")

    assert isinstance(exc, ValidationError)
    assert exc.label == "num"
    assert exc.value == -5


# ==============================================================================
# 3. INTERACTION WITH CONTAINERS
# ==============================================================================

def test_described_is_not_flattened_by_containers(subtests):
    """Verify that AllOf / AnyOf keep a Described operand whole instead of unwrapping it."""

    with subtests.test("AllOf"):
        described = Described(AllOf(is_a, is_b), "ab")
        rule = AllOf(described, is_c)
        assert rule.rules == (described, is_c)

    with subtests.test("AnyOf"):
        described = Described(AnyOf(is_a, is_b), "ab")
        rule = AnyOf(described, is_c)
        assert rule.rules == (described, is_c)


def test_described_text_is_used_by_containers(subtests):
    """Verify that containers describe a Described operand by its text."""
    described = Described(AllOf(is_a, is_b), "list[int]")

    with subtests.test("AllOf"):
        assert AllOf(described, is_c).describe() == "list[int] & is_c"

    with subtests.test("AnyOf"):
        assert AnyOf(described, is_c).describe() == "list[int] | is_c"
