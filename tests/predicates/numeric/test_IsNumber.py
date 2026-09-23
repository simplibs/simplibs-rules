"""Tests for the IsNumber rule."""

from decimal import Decimal
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric.IsNumber import IsNumber, is_number


def test_is_number_contract(subtests):
    """Verify the complete contract of the IsNumber rule."""
    rule = IsNumber()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[10, 10.5, Decimal("10.5"), complex(1, 2)],
        invalid_values=[True, False, "10", None, []],
        deep_check=True,
        verbose=False,
    )


def test_is_number_exception(subtests):
    """Verify diagnosis (TypeError) for non-numeric value."""
    rule = IsNumber()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("123", Kwargs(value_name="amount")),
        exception_type=ValidationError,
        label="amount",
        value="123",
        error_name="IS_NUMBER_ERROR",
        expected="a number",
        problem="Value '123' of type 'str' is not a numeric value.",
        how_to_fix="Provide a numeric value (int, float, Decimal, complex; booleans excluded).",
        exception=TypeError,
        verbose=False,
    )


def test_is_number_helper():
    """Verify helper function is_number."""
    assert is_number(10) is True
    assert is_number(Decimal("1.2")) is True
    assert is_number(True) is False