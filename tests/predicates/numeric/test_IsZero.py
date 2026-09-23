"""Tests for the IsZero rule."""

from decimal import Decimal
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsZero


def test_is_zero_contract(subtests):
    """Verify the complete contract of the IsZero rule."""
    rule = IsZero()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[0, 0.0, Decimal("0"), complex(0, 0)],
        invalid_values=[1, 0.1, Decimal("0.1"), complex(1, 0), True, False, "0", None],
        deep_check=True,
        verbose=False,
    )


def test_is_zero_exception_type_error(subtests):
    """Verify diagnosis (TypeError) for non-numeric type."""
    rule = IsZero()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("0", Kwargs(value_name="balance")),
        exception_type=ValidationError,
        label="balance",
        value="0",
        error_name="IS_ZERO_ERROR",
        expected="numeric zero",
        problem="Value '0' of type 'str' is not a numeric value.",
        how_to_fix="Provide a numeric value equal to 0 (int, float, Decimal, or complex).",
        exception=TypeError,
        verbose=False,
    )


def test_is_zero_exception_value_error(subtests):
    """Verify diagnosis (ValueError) for non-zero number."""
    rule = IsZero()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(42, Kwargs(value_name="offset")),
        exception_type=ValidationError,
        label="offset",
        value=42,
        error_name="IS_ZERO_ERROR",
        expected="zero",
        problem="Value 42 is not zero.",
        how_to_fix="Provide a numeric value equal to 0.",
        exception=ValueError,
        verbose=False,
    )