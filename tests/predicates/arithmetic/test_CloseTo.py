"""Tests for the CloseTo arithmetic rule."""

import math
from typing import Any
import pytest

# Test tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.predicates.arithmetic import CloseTo


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_close_to_contract(subtests):
    """Verify the complete contract of CloseTo rule using master orchestrator."""
    rule = CloseTo(10.0, rel_tol=0.1)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[10.0, 10.5, 9.5, 10],
        invalid_values=[12.0, 8.0, "10.0", None, True],
        rule_factory=CloseTo,
        invalid_init_params=[
            (("invalid_target",), {}),             # Non-numeric target raises ParamError
            ((10.0,), {"rel_tol": "invalid"}),     # Non-numeric rel_tol raises ParamError
            ((10.0,), {"abs_tol": None}),          # Non-numeric abs_tol raises ParamError
            ((10.0,), {"rel_tol": True}),          # Bool rel_tol raises ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_close_to_value_out_of_tolerance_exception(subtests):
    """Verify diagnosis upon failure due to exceeding tolerated difference (ValueError)."""
    rule = CloseTo(100.0, rel_tol=0.01)  # Accepts approximately 99.0 to 101.0

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(105.0, Kwargs(value_name="measurement")),
        exception_type=ValidationError,
        label="measurement",
        value=105.0,
        error_name="CLOSE_TO_ERROR",
        expected="value close to 100.0",
        problem="Value 105.0 is not close to 100.0 (tolerance: rel=0.01).",
        how_to_fix="Provide a value approximately equal to 100.0.",
        exception=ValueError,
        verbose=False,
    )


def test_close_to_abs_tolerance_exception_formatting(subtests):
    """Verify correct text formatting of tolerances in exception when abs_tol is also provided."""
    rule = CloseTo(10.0, rel_tol=1e-9, abs_tol=0.5)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(11.0, Kwargs(value_name="weight")),
        exception_type=ValidationError,
        label="weight",
        value=11.0,
        error_name="CLOSE_TO_ERROR",
        expected="value close to 10.0",
        problem="Value 11.0 is not close to 10.0 (tolerance: rel=1e-09, abs=0.5).",
        how_to_fix="Provide a value approximately equal to 10.0.",
        exception=ValueError,
        verbose=False,
    )


def test_close_to_type_error_exception(subtests):
    """Verify that passing a non-numeric value raises an exception wrapped in TypeError."""
    rule = CloseTo(3.14)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("3.14", Kwargs(value_name="pi_val")),
        exception_type=ValidationError,
        label="pi_val",
        value="3.14",
        error_name="CLOSE_TO_ERROR",
        expected="value close to 3.14",
        problem="Value '3.14' of type 'str' is not a primitive number.",
        how_to_fix="Provide a primitive numeric value (int or float).",
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. SPECIFIC EDGE CASES & FUNCTIONALITY
# ==============================================================================

def test_close_to_math_pi_example():
    """Verify functionality with known constants like math.pi."""
    rule = CloseTo(math.pi, rel_tol=1e-3)

    assert rule.is_valid(3.14159) is True
    assert rule.is_valid(3.14) is True
    assert rule.is_valid(3.1) is False


def test_close_to_absolute_tolerance_only():
    """Verify functionality when using absolute tolerance boundary exclusively."""
    rule = CloseTo(0.0, rel_tol=0.0, abs_tol=0.01)

    assert rule.is_valid(0.005) is True
    assert rule.is_valid(-0.008) is True
    assert rule.is_valid(0.02) is False