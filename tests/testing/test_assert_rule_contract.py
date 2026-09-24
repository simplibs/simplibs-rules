"""Tests for the master assert_rule_contract orchestrator function."""

from typing import Any
import pytest
from _pytest.outcomes import Failed

from simplibs.exception import ParamError, ValidationError
from simplibs.rules.base_class import Rule
from simplibs.rules.testing.assert_rule_contract import assert_rule_contract


# --- Mock Rules for Testing ---

class DummyValidRule(Rule):
    """Fully valid rule meeting the complete contract."""
    def __init__(self, limit: int = 10):
        if limit <= 0:
            raise ParamError("limit must be positive")
        self.limit = limit

    def is_valid(self, value: Any) -> bool:
        return isinstance(value, int) and value <= self.limit

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        return ValidationError(
            problem="Value exceeds limit or is not int.",
            expected=f"Integer <= {self.limit}",
            how_to_fix="Provide a smaller integer.",
            label=value_name,
            value=value,
            context=context,
            error_name="DUMMY_LIMIT_ERROR",
        )


class DummyCompoundRule(Rule):
    """Rule returning different error names based on input value."""
    def is_valid(self, value: Any) -> bool:
        return False

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        err_name = "LIMIT_ERROR" if isinstance(value, int) else "TYPE_ERROR"
        return ValidationError(
            problem="Value is invalid.",
            expected="Valid integer.",
            how_to_fix="Provide integer.",
            label=value_name,
            value=value,
            context=context,
            error_name=err_name,
        )


class DummyTransformingRule(Rule):
    """Rule that transforms input string into int in exception (e.g. Compose)."""
    def is_valid(self, value: Any) -> bool:
        return False

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        transformed = int(value) if isinstance(value, str) and value.lstrip("-").isdigit() else value
        return ValidationError(
            problem="Transformed value is invalid.",
            expected="Positive integer.",
            how_to_fix="Provide valid input.",
            label=value_name,
            value=transformed,  # Returns transformed int instead of str
            context=context,
        )


class DummyBrokenIsValidRule(Rule):
    """Rule with faulty is_valid implementation (returns non-bool)."""
    def is_valid(self, value: Any) -> bool:
        return 1 if value == 5 else 0  # type: ignore # Returns int instead of bool

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        return ValidationError("Error")


class DummyBrokenValidateRule(Rule):
    """Rule with faulty validate method (does not return value when return_value=True)."""
    def validate(self, value: Any, return_value: bool = False, return_bool: bool = False) -> Any:
        if return_value:
            return "BROKEN"
        return super().validate(value, return_value=return_value, return_bool=return_bool)

    def is_valid(self, value: Any) -> bool:
        return value == 5

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        return ValidationError("Error")


class DummyBrokenBuildExceptionRule(Rule):
    """Rule returning a different error_name than expected_error_name."""
    def is_valid(self, value: Any) -> bool:
        return value == 5

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        return ValidationError(
            problem="Error",
            expected="5",
            how_to_fix="Provide 5",
            label=value_name,
            value=value,
            context=context,
            error_name="ACTUAL_NAME",
        )


class DummyBrokenConstructorRule(Rule):
    """Rule whose constructor fails to raise ParamError for invalid arguments."""
    def __init__(self, limit: int = 10):
        pass  # Ignores negative limit and does not raise ParamError

    def is_valid(self, value: Any) -> bool:
        return True

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        return ValidationError("Error")


# --- Tests ---

def test_assert_rule_contract_fails_on_non_rule_instance(subtests):
    """Verify fail-fast type guard when a non-Rule instance is passed."""
    with pytest.raises(AssertionError, match="expects a Rule instance"):
        assert_rule_contract(
            subtests,
            rule="not_a_rule",  # type: ignore
            valid_values=[1],
            invalid_values=[2],
            verbose=False
        )


def test_assert_rule_contract_full_success(subtests):
    """Verify complete successful run through all 4 orchestrator stages."""
    rule = DummyValidRule(limit=10)
    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 5, 10],
        invalid_values=[11, "invalid", None],
        expected_error_name="DUMMY_LIMIT_ERROR",
        rule_factory=DummyValidRule,
        invalid_init_params=[
            ((-5,), {}),  # limit <= 0 -> ParamError
        ],
        deep_check=True,
        verbose=False,
    )


def test_assert_rule_contract_sequence_expected_error_name_success(subtests):
    """Verify orchestrator passing sequences of expected_error_name through to build_exception."""
    rule = DummyCompoundRule()
    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[],
        invalid_values=[15, "str_val"],
        expected_error_name=["LIMIT_ERROR", "TYPE_ERROR"],
        deep_check=True,
        verbose=False,
    )


def test_assert_rule_contract_transforming_rule_fails_by_default(subtests):
    """Verify that a transforming rule fails under default check_value=True."""
    rule = DummyTransformingRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_contract(
            subtests,
            rule=rule,
            valid_values=[],
            invalid_values=["-5"],
            check_value=True,
            verbose=False
        )


def test_assert_rule_contract_transforming_rule_passes_when_check_value_disabled(subtests):
    """Verify that a transforming rule passes through orchestrator with check_value=False."""
    rule = DummyTransformingRule()
    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[],
        invalid_values=["-5"],
        check_value=False,
        verbose=False,
    )


def test_assert_rule_contract_fails_on_is_valid_stage(subtests):
    """Verify error catching in Stage 1 (is_valid)."""
    rule = DummyBrokenIsValidRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_contract(
            subtests,
            rule=rule,
            valid_values=[5],
            invalid_values=[10],
            verbose=False,
        )


def test_assert_rule_contract_fails_on_validate_stage(subtests):
    """Verify error catching in Stage 2 (validate)."""
    rule = DummyBrokenValidateRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_contract(
            subtests,
            rule=rule,
            valid_values=[5],
            invalid_values=[10],
            verbose=False,
        )


def test_assert_rule_contract_fails_on_build_exception_stage(subtests):
    """Verify error catching in Stage 3 (build_exception - e.g. error_name mismatch)."""
    rule = DummyBrokenBuildExceptionRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_contract(
            subtests,
            rule=rule,
            valid_values=[5],
            invalid_values=[10],
            expected_error_name="EXPECTED_NAME",  # Returns ACTUAL_NAME
            verbose=False,
        )


def test_assert_rule_contract_fails_on_param_error_stage(subtests):
    """Verify error catching in Stage 4 (constructor requiring ParamError)."""
    rule = DummyBrokenConstructorRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_contract(
            subtests,
            rule=rule,
            valid_values=[5],
            invalid_values=[10],
            rule_factory=DummyBrokenConstructorRule,
            invalid_init_params=[((-5,), {})],  # Ignored -> failure
            verbose=False,
        )