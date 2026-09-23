"""Tests for the IsDecimal rule."""

from decimal import Decimal
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsDecimal


def test_is_decimal_contract(subtests):
    """Verify the complete contract of the IsDecimal rule."""
    rule = IsDecimal()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[Decimal("0"), Decimal("10.5"), Decimal("-1.23")],
        invalid_values=[10, 10.5, "10.5", True, None, []],
        deep_check=True,
        verbose=False,
    )


def test_is_decimal_exception(subtests):
    """Verify diagnosis (TypeError) when non-Decimal object is supplied."""
    rule = IsDecimal()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(10.5, Kwargs(value_name="price")),
        exception_type=ValidationError,
        label="price",
        value=10.5,
        error_name="IS_DECIMAL_ERROR",
        expected="decimal.Decimal",
        problem="Value 10.5 of type 'float' is not a Decimal.",
        how_to_fix="Provide a decimal.Decimal value (e.g. Decimal('10.5')).",
        exception=TypeError,
        verbose=False,
    )