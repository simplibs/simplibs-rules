"""Tests for the assert_rule_slots function."""

from typing import Any
import pytest
from simplibs.rules.base_class import Rule
from simplibs.rules.testing.asserts.assert_rule_slots import assert_rule_slots


# ----------------------------------------------------------------------
# Dummy Rules for Testing
# ----------------------------------------------------------------------

class DummyEmptySlotsRule(Rule):
    """Correct rule: declares empty __slots__ and adds no attributes."""

    __slots__ = ()

    def is_valid(self, value: Any) -> bool:
        return True

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        raise NotImplementedError


class DummyAttributeSlotsRule(Rule):
    """Correct rule: declares its attribute in __slots__."""

    __slots__ = ("limit",)

    def __init__(self, limit: int = 10) -> None:
        self.limit = limit

    def is_valid(self, value: Any) -> bool:
        return True

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        raise NotImplementedError


class DummyNoSlotsRule(Rule):
    """Broken rule: forgot __slots__ entirely."""

    def is_valid(self, value: Any) -> bool:
        return True

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        raise NotImplementedError


class _DummyBaseWithoutSlots(Rule):
    """Broken base: no __slots__, so every subclass instance regains a __dict__."""

    def is_valid(self, value: Any) -> bool:
        return True

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        raise NotImplementedError


class DummyChildWithSlotsRule(_DummyBaseWithoutSlots):
    """Broken by inheritance: declares __slots__ itself, but its base does not."""

    __slots__ = ("limit",)

    def __init__(self, limit: int = 10) -> None:
        self.limit = limit


# ----------------------------------------------------------------------
# Tests for assert_rule_slots
# ----------------------------------------------------------------------

def test_assert_rule_slots_empty_slots_passes(subtests):
    """Verify that a rule with empty __slots__ passes."""
    assert_rule_slots(subtests, DummyEmptySlotsRule())


def test_assert_rule_slots_attribute_slots_passes(subtests):
    """Verify that a rule declaring its attributes in __slots__ passes."""
    assert_rule_slots(subtests, DummyAttributeSlotsRule())


def test_assert_rule_slots_type_guard_fails(subtests):
    """Verify fail-fast type guard when rule is not a Rule instance."""
    with pytest.raises(AssertionError, match="expects a Rule instance"):
        assert_rule_slots(
            subtests,
            rule="not_a_rule",  # type: ignore
            verbose=False,
        )


def test_assert_rule_slots_missing_slots_fails(subtests):
    """Verify failure when a rule has a __dict__, and that the message names the class."""
    with pytest.raises(AssertionError, match="__dict__") as excinfo:
        assert_rule_slots(subtests, DummyNoSlotsRule(), verbose=False)

    assert "DummyNoSlotsRule" in str(excinfo.value)


def test_assert_rule_slots_slotless_base_class_fails(subtests):
    """Verify failure when only a base class lacks __slots__, and that the base is named as the offender."""
    with pytest.raises(AssertionError, match="__dict__") as excinfo:
        assert_rule_slots(subtests, DummyChildWithSlotsRule(), verbose=False)

    message = str(excinfo.value)
    assert "Classes without __slots__:" in message

    offenders = message.split("Classes without __slots__:")[1]
    assert "_DummyBaseWithoutSlots" in offenders
    assert "DummyChildWithSlotsRule" not in offenders
