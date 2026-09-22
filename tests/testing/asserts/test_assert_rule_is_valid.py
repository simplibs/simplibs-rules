"""Tests for the assert_rule_is_valid function."""

from typing import Any
import pytest
from simplibs.rules.base_class import Rule
from simplibs.rules.testing.asserts.assert_rule_is_valid import assert_rule_is_valid


# ----------------------------------------------------------------------
# Dummy Rules for Testing
# ----------------------------------------------------------------------

class DummyValidRule(Rule):
    """Correct Rule implementation."""

    def is_valid(self, value: Any) -> bool:
        return value == "valid"

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        raise NotImplementedError


class DummyTruthyRule(Rule):
    """Broken Rule: returns truthy integers (1 / 0) instead of strict booleans."""

    def is_valid(self, value: Any) -> bool:
        return 1 if value == "valid" else 0

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        raise NotImplementedError


class DummyInconsistentCallRule(Rule):
    """Broken Rule: __call__ does not match is_valid()."""

    def is_valid(self, value: Any) -> bool:
        return value == "valid"

    def __call__(self, value: Any) -> bool:
        return False  # Always returns False regardless of input

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        raise NotImplementedError


class DummyRaisingRule(Rule):
    """Broken Rule: raises an exception during is_valid() evaluation."""

    def is_valid(self, value: Any) -> bool:
        if value == "invalid":
            raise ValueError("Unexpected failure during evaluation")
        return True

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        raise NotImplementedError


# ----------------------------------------------------------------------
# Tests for assert_rule_is_valid
# ----------------------------------------------------------------------

def test_assert_rule_is_valid_success(subtests):
    """Verify that a compliant Rule passes all positive and negative checks."""
    rule = DummyValidRule()

    # Should complete with no assertion errors
    assert_rule_is_valid(
        subtests,
        rule=rule,
        valid_values=["valid"],
        invalid_values=["invalid", 123, None],
    )


def test_assert_rule_is_valid_type_guard_fails(subtests):
    """Verify fail-fast type guard when rule is not a Rule instance."""
    with pytest.raises(AssertionError, match="expects a Rule instance"):
        assert_rule_is_valid(
            subtests,
            rule="not_a_rule",  # type: ignore
            valid_values=[1],
            invalid_values=[2],
            verbose=False,
        )


def test_assert_rule_is_valid_non_strict_bool_fails(subtests):
    """Verify failure when is_valid returns truthy non-bool values (e.g. 1 instead of True)."""
    rule = DummyTruthyRule()

    with pytest.raises(AssertionError):
        assert_rule_is_valid(
            subtests,
            rule=rule,
            valid_values=["valid"],
            invalid_values=["invalid"],
            verbose=False,
        )


def test_assert_rule_is_valid_inconsistent_call_fails(subtests):
    """Verify failure when __call__ shortcut behaves differently than is_valid()."""
    rule = DummyInconsistentCallRule()

    with pytest.raises(AssertionError):
        assert_rule_is_valid(
            subtests,
            rule=rule,
            valid_values=["valid"],
            invalid_values=["invalid"],
            verbose=False,
        )


def test_assert_rule_is_valid_unexpected_raise_fails(subtests):
    """Verify failure when is_valid() raises an unhandled exception for an invalid value."""
    rule = DummyRaisingRule()

    with pytest.raises(ValueError, match="Unexpected failure during evaluation"):
        assert_rule_is_valid(
            subtests,
            rule=rule,
            valid_values=["valid"],
            invalid_values=["invalid"],
            verbose=False,
        )