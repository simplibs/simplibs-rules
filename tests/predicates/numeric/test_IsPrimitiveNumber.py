"""Tests for the IsPrimitiveNumber rule."""

from decimal import Decimal
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric.IsPrimitiveNumber import (
    IsPrimitiveNumber,
    is_primitive_number,
)


def test_is_primitive_number_contract(subtests):
    """Verify the complete contract of the IsPrimitiveNumber rule."""
    rule = IsPrimitiveNumber()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[0, 10, -5, 0.0, 10.5, -1.23],
        invalid_values=[Decimal("10.5"), complex(1, 2), True, "10", None, []],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_primitive_number_exception(subtests):
    """Verify diagnosis (TypeError) for a non-primitive numeric value."""
    rule = IsPrimitiveNumber()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(Decimal("10"), Kwargs(value_name="score")),
        exception_type=ValidationError,
        label="score",
        value=Decimal("10"),
        error_name="IS_PRIMITIVE_NUMBER_ERROR",
        expected="a primitive number (int or float)",
        problem="Value Decimal('10') of type 'Decimal' is not a primitive number (int, float).",
        how_to_fix="Provide a primitive numeric value (int or float; booleans excluded).",
        exception=TypeError,
        verbose=False,
    )


def test_is_primitive_number_helper():
    """Verify helper function is_primitive_number."""
    assert is_primitive_number(5) is True
    assert is_primitive_number(5.5) is True
    assert is_primitive_number(Decimal("5")) is False