"""Tests for the assert_rule_build_exception function."""

from typing import Any
import pytest
from _pytest.outcomes import Failed

from simplibs.exception import ValidationError
from simplibs.rules.base_class import Rule
from simplibs.rules.testing.asserts.assert_rule_build_exception import (
    assert_rule_build_exception,
)


# --- Mock Rules for Testing ---

class DummyValidRule(Rule):
    """Fully valid rule with a complete diagnostic card."""
    def is_valid(self, value: Any) -> bool:
        return value == "valid"

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        return ValidationError(
            problem="Value is invalid.",
            expected="Value must be 'valid'.",
            how_to_fix="Provide 'valid'.",
            label=value_name,
            value=value,
            context=context,
            error_name="DUMMY_ERROR",
            exception=TypeError,
        )


class DummyTransformingRule(Rule):
    """Rule that transforms the perceived value (e.g. string "-5" to int -5)."""
    def is_valid(self, value: Any) -> bool:
        return False

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        transformed_value = int(value) if isinstance(value, str) and value.lstrip("-").isdigit() else value
        return ValidationError(
            problem="Transformed value is invalid.",
            expected="Positive number.",
            how_to_fix="Fix it.",
            label=value_name,
            value=transformed_value,  # Returns transformed value!
            context=context,
        )


class DummyNonValidationErrorRule(Rule):
    """Rule that raises a regular TypeError instead of ValidationError."""
    def is_valid(self, value: Any) -> bool:
        return False

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> Exception:
        return TypeError("Not a ValidationError instance")  # type: ignore


class DummyWrongMetadataRule(Rule):
    """Rule with incorrect error_name and exception type."""
    def is_valid(self, value: Any) -> bool:
        return False

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        return ValidationError(
            problem="Value is invalid.",
            expected="Value must be valid.",
            how_to_fix="Fix it.",
            label=value_name,
            value=value,
            context=context,
            error_name="WRONG_NAME",
            exception=ValueError,
        )


class DummyEmptyDiagnosticsRule(Rule):
    """Rule with empty diagnostic texts (fails when deep_check=True)."""
    def is_valid(self, value: Any) -> bool:
        return False

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        return ValidationError(
            problem="",  # Empty text -> diagnostic card violation
            expected="",
            how_to_fix="",
            label=value_name,
            value=value,
            context=context,
        )


# --- Tests ---

def test_assert_rule_build_exception_success(subtests):
    """Verify a fully functional rule with a correctly built exception."""
    rule = DummyValidRule()
    assert_rule_build_exception(
        subtests,
        rule=rule,
        invalid_values=["invalid_1", "invalid_2"],
        expected_error_name="DUMMY_ERROR",
        expected_exception_type=TypeError,
        deep_check=True,
    )


def test_assert_rule_build_exception_transforming_rule_fails_by_default(subtests):
    """Verify that a transforming rule fails when check_value=True (default state)."""
    rule = DummyTransformingRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_build_exception(
            subtests,
            rule=rule,
            invalid_values=["-5"],  # Rule returns int(-5), but str("-5") is expected
            check_value=True,
            verbose=False,
        )


def test_assert_rule_build_exception_transforming_rule_passes_when_check_value_disabled(subtests):
    """Verify that a transforming rule passes when value checking is disabled (check_value=False)."""
    rule = DummyTransformingRule()
    assert_rule_build_exception(
        subtests,
        rule=rule,
        invalid_values=["-5"],
        check_value=False,
    )


def test_assert_rule_build_exception_fails_on_non_validate_error(subtests):
    """Verify failure when build_exception does not return a ValidationError."""
    rule = DummyNonValidationErrorRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_build_exception(
            subtests,
            rule=rule,  # type: ignore
            invalid_values=["invalid"],
            verbose=False,
        )


def test_assert_rule_build_exception_fails_on_mismatched_error_name(subtests):
    """Verify failure on mismatched expected_error_name."""
    rule = DummyWrongMetadataRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_build_exception(
            subtests,
            rule=rule,
            invalid_values=["invalid"],
            expected_error_name="EXPECTED_NAME",  # Rule returns WRONG_NAME
            verbose=False,
        )


def test_assert_rule_build_exception_fails_on_mismatched_exception_type(subtests):
    """Verify failure on mismatched expected_exception_type."""
    rule = DummyWrongMetadataRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_build_exception(
            subtests,
            rule=rule,
            invalid_values=["invalid"],
            expected_exception_type=TypeError,  # Rule returns ValueError
            verbose=False,
        )


def test_assert_rule_build_exception_fails_on_empty_diagnostics(subtests):
    """Verify failure during deep_check=True when diagnostic fields are empty."""
    rule = DummyEmptyDiagnosticsRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_build_exception(
            subtests,
            rule=rule,
            invalid_values=["invalid"],
            deep_check=True,
            verbose=False,
        )


def test_assert_rule_build_exception_passes_empty_diagnostics_when_deep_check_disabled(subtests):
    """Verify that empty diagnostics pass when deep_check=False."""
    rule = DummyEmptyDiagnosticsRule()
    assert_rule_build_exception(
        subtests,
        rule=rule,
        invalid_values=["invalid"],
        deep_check=False,
    )