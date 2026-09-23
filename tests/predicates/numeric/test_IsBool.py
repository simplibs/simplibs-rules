"""Tests for the IsBool rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.numeric import IsBool


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_is_bool_contract(subtests):
    """Verify the complete contract of the IsBool rule using the master orchestrator."""
    rule = IsBool()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[True, False],  # Strict boolean only
        invalid_values=[
            1,
            0,
            1.0,
            0.0,
            "True",
            "False",
            [True],
            None,
            {},
        ],  # Ints (even though bool inherits from int in Python), floats, strs, etc. must fail
        rule_factory=IsBool,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_is_bool_exception_details(subtests):
    """Verify exact diagnostic card details upon validation failure."""
    rule = IsBool()

    # Test 1: Integer input (1) - common pitfall due to bool subclassing int
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(1, Kwargs(value_name="is_active", context="user_profile")),
        exception_type=ValidationError,
        error_name="IS_BOOL_ERROR",
        label="is_active",
        expected="a boolean (True or False)",
        problem="Value 1 of type 'int' is not a boolean.",
        context="user_profile",
        how_to_fix="Provide a boolean value (True or False).",
        exception=TypeError,
    )

    # Test 2: String input ("True")
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("True", Kwargs(value_name="flag")),
        exception_type=ValidationError,
        error_name="IS_BOOL_ERROR",
        label="flag",
        expected="a boolean (True or False)",
        problem="Value 'True' of type 'str' is not a boolean.",
        how_to_fix="Provide a boolean value (True or False).",
        exception=TypeError,
    )