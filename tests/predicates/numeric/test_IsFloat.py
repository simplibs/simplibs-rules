"""Tests for the IsFloat rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsFloat


def test_is_float_contract(subtests):
    """Verify the complete contract of the IsFloat rule."""
    rule = IsFloat()

    assert_rule_contract(
        subtests,
        rule=rule,
        # float("nan") excluded because NaN == NaN returns False per IEEE 754
        valid_values=[0.0, 10.5, -1.23, float("inf")],
        invalid_values=[10, "10.5", True, None, []],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_float_exception(subtests):
    """Verify diagnosis (TypeError) when non-float value is given."""
    rule = IsFloat()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(10, Kwargs(value_name="ratio")),
        exception_type=ValidationError,
        label="ratio",
        value=10,
        error_name="IS_FLOAT_ERROR",
        expected="a float",
        problem="Value 10 of type 'int' is not a float.",
        how_to_fix="Provide a float value (e.g. 10.5).",
        exception=TypeError,
        verbose=False,
    )