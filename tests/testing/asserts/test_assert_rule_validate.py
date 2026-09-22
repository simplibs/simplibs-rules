"""Tests for the assert_rule_validate function."""

from typing import Any
import pytest
from _pytest.outcomes import Failed

from simplibs.exception import ValidationError
from simplibs.rules.base_class import Rule
from simplibs.rules.testing.asserts.assert_rule_validate import assert_rule_validate


# --- Mock Rules for Testing ---

class DummyValidRule(Rule):
    """Correct rule meeting all validate() contracts."""
    def is_valid(self, value: Any) -> bool:
        return value == "valid"

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        return ValidationError("Invalid value")


class DummyBadReturnValueRule(Rule):
    """Rule that fails to return the original value when return_value=True."""
    def validate(self, value: Any, return_value: bool = False, return_bool: bool = False) -> Any:
        if return_value:
            return "MUTATED_VALUE"  # Contract violation
        return super().validate(value, return_value=return_value, return_bool=return_bool)

    def is_valid(self, value: Any) -> bool:
        return value == "valid"

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        return ValidationError("Invalid value")


class DummyNoRaiseOnInvalidRule(Rule):
    """Rule that fails to raise ValidationError for an invalid value."""
    def validate(self, value: Any, return_value: bool = False, return_bool: bool = False) -> Any:
        if not self.is_valid(value) and not return_bool:
            return True  # Returns True instead of raising an exception
        return super().validate(value, return_value=return_value, return_bool=return_bool)

    def is_valid(self, value: Any) -> bool:
        return value == "valid"

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        return ValidationError("Invalid value")


class DummyBadReturnBoolRule(Rule):
    """Rule that fails to return False when return_bool=True on an invalid value."""
    def validate(self, value: Any, return_value: bool = False, return_bool: bool = False) -> Any:
        if return_bool and not self.is_valid(value):
            return "NOT_A_BOOL"  # Contract violation
        return super().validate(value, return_value=return_value, return_bool=return_bool)

    def is_valid(self, value: Any) -> bool:
        return value == "valid"

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        return ValidationError("Invalid value")


# --- Tests ---

def test_assert_rule_validate_success(subtests):
    """Verify that a fully valid rule passes all validate() matrices."""
    rule = DummyValidRule()
    assert_rule_validate(
        subtests,
        rule=rule,
        valid_values=["valid"],
        invalid_values=["invalid", 123, None],
    )


def test_assert_rule_validate_fails_on_bad_return_value(subtests):
    """Verify failure when rule.validate(val, return_value=True) does not return val."""
    rule = DummyBadReturnValueRule()
    with pytest.raises(AssertionError):
        assert_rule_validate(
            subtests,
            rule=rule,
            valid_values=["valid"],
            invalid_values=["invalid"],
            verbose=False,
        )


def test_assert_rule_validate_fails_on_missing_exception(subtests):
    """Verify failure when an invalid value does not trigger ValidationError in standard mode."""
    rule = DummyNoRaiseOnInvalidRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_validate(
            subtests,
            rule=rule,
            valid_values=["valid"],
            invalid_values=["invalid"],
            verbose=False,
        )


def test_assert_rule_validate_fails_on_bad_return_bool(subtests):
    """Verify failure when rule.validate(val, return_bool=True) does not return False for an invalid value."""
    rule = DummyBadReturnBoolRule()
    with pytest.raises(AssertionError):
        assert_rule_validate(
            subtests,
            rule=rule,
            valid_values=["valid"],
            invalid_values=["invalid"],
            verbose=False,
        )