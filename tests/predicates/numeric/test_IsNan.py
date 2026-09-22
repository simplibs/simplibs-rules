"""Tests for the IsNan rule."""

import math
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsNan


def test_is_nan_contract(subtests):
    """Verify contract for IsNan without relying on generic assert_rule_contract (handles IEEE 754 nan != nan)."""
    rule = IsNan()

    # 1. Valid input test (float NaN)
    with subtests.test("valid_input_nan"):
        val = float("nan")
        assert rule.is_valid(val) is True
        assert rule.validate(val) is True

        returned_val = rule.validate(val, return_value=True)
        assert isinstance(returned_val, float)
        assert math.isnan(returned_val)  # Used instead of `== val`, which fails

    # 2. Invalid inputs test
    invalid_values = [0.0, 10.5, float("inf"), 10, "nan", True, None]
    for invalid_val in invalid_values:
        with subtests.test(f"invalid_input_{invalid_val!r}"):
            assert rule.is_valid(invalid_val) is False
            with pytest.raises(ValidationError):
                rule.validate(invalid_val)


def test_is_nan_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when value is not a float."""
    rule = IsNan()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("nan", Kwargs(value_name="val")),
        exception_type=ValidationError,
        label="val",
        value="nan",
        error_name="IS_NAN_ERROR",
        expected="float('nan')",
        problem="Value 'nan' is of type 'str', expected float.",
        how_to_fix="Provide float('nan').",
        exception=TypeError,
        verbose=False,
    )


def test_is_nan_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when value is a non-NaN float."""
    rule = IsNan()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(1.23, Kwargs(value_name="val")),
        exception_type=ValidationError,
        label="val",
        value=1.23,
        error_name="IS_NAN_ERROR",
        expected="float('nan')",
        problem="Value 1.23 is a regular (non-NaN) float.",
        how_to_fix="Provide float('nan').",
        exception=ValueError,
        verbose=False,
    )