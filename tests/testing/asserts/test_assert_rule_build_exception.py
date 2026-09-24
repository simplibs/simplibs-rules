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


class DummyCompoundRule(Rule):
    """Rule that returns different error names and exception types based on input value."""
    def is_valid(self, value: Any) -> bool:
        return False

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        if value == "invalid_1":
            err_name = "FIRST_ERROR"
            exc_type = TypeError
        else:
            err_name = "SECOND_ERROR"
            exc_type = ValueError

        return ValidationError(
            problem="Value is invalid.",
            expected="Valid value.",
            how_to_fix="Fix it.",
            label=value_name,
            value=value,
            context=context,
            error_name=err_name,
            exception=exc_type,
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


def test_assert_rule_build_exception_sequence_success(subtests):
    """Verify sequence-based expected_error_name and expected_exception_type matching per index."""
    rule = DummyCompoundRule()
    assert_rule_build_exception(
        subtests,
        rule=rule,
        invalid_values=["invalid_1", "invalid_2"],
        expected_error_name=["FIRST_ERROR", "SECOND_ERROR"],
        expected_exception_type=(TypeError, ValueError),
        deep_check=True,
    )


def test_assert_rule_build_exception_sequence_with_none_elements(subtests):
    """Verify sequence matching when some elements are None (bypassing check for specific index)."""
    rule = DummyCompoundRule()
    assert_rule_build_exception(
        subtests,
        rule=rule,
        invalid_values=["invalid_1", "invalid_2"],
        expected_error_name=["FIRST_ERROR", None],  # Second item error_name not checked
        expected_exception_type=[None, ValueError],  # First item exception_type not checked
        deep_check=True,
    )


def test_assert_rule_build_exception_sequence_length_mismatch_error_name(subtests):
    """Verify ValueError when expected_error_name sequence length doesn't match invalid_values."""
    rule = DummyCompoundRule()
    with pytest.raises(ValueError, match="expected_error_name sequence must have the same length"):
        assert_rule_build_exception(
            subtests,
            rule=rule,
            invalid_values=["invalid_1", "invalid_2"],
            expected_error_name=["ONLY_ONE_ERROR"],  # Length 1 vs 2 invalid values
        )


def test_assert_rule_build_exception_sequence_length_mismatch_exception_type(subtests):
    """Verify ValueError when expected_exception_type sequence length doesn't match invalid_values."""
    rule = DummyCompoundRule()
    with pytest.raises(ValueError, match="expected_exception_type sequence must have the same length"):
        assert_rule_build_exception(
            subtests,
            rule=rule,
            invalid_values=["invalid_1", "invalid_2"],
            expected_exception_type=[TypeError, ValueError, KeyError],  # Length 3 vs 2
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