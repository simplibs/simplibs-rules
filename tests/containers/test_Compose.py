"""Tests for the Compose container rule."""

from typing import Any
import pytest

# Testing tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.containers import Compose
from simplibs.rules.predicates.comparisons import GreaterThan


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_compose_contract(subtests):
    """Verify the complete contract of Compose using the master orchestrator."""
    # Transforms string to int (int("10")) and then verifies that int is > 0
    rule = Compose(int, GreaterThan(0))

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["10", "42", 5],               # Transformation succeeds and value is > 0
        invalid_values=["-5", "invalid", None],     # Either int() fails or value is <= 0
        rule_factory=Compose,
        invalid_init_params=[
            (("not_callable", GreaterThan(0)), {}),  # Non-callable transformer raises ParamError
            ((int, "not_callable"), {}),             # Non-callable validator raises ParamError
        ],
        deep_check=True,
        check_value=False,  # Compose passes transformed value to exception (int -5 instead of str "-5")
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST (Transformation vs Validation)
# ==============================================================================

def test_compose_transformation_failure_exception(subtests):
    """Verify diagnostic card details when the transformer itself fails (e.g., int('abc'))."""
    rule = Compose(int, GreaterThan(0))

    # Transformer failure int("abc") raises ValueError, wrapped in TypeError by Compose
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("abc", Kwargs(value_name="raw_input")),
        exception_type=ValidationError,
        error_name="COMPOSE_TRANSFORM_FAILED_ERROR",
        label="raw_input",
        expected="value compatible with transformer",
        problem="Transformation by",
        how_to_fix="Provide a value that can be transformed",
        exception=TypeError,
        verbose=False,
    )


def test_compose_delegates_validator_exception(subtests):
    """Verify that Compose delegates diagnostics to validator after successful transformation."""
    rule = Compose(int, GreaterThan(0))

    # "0" successfully converts to int 0, but GreaterThan(0) fails
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("0", Kwargs(value_name="score")),
        exception_type=ValidationError,
        label="score",
        expected="greater than 0",
        verbose=False,
    )


# ==============================================================================
# 3. EDGE CASES & TRANSFORMATION BEHAVIOR
# ==============================================================================

def test_compose_custom_lambda_transformer():
    """Verify functionality with anonymous lambda transformer and data extraction."""
    rule = Compose(len, GreaterThan(2))

    assert rule.is_valid("hello") is True   # len = 5 > 2
    assert rule.is_valid("hi") is False      # len = 2, not > 2
    assert rule.is_valid(12345) is False     # len(12345) raises TypeError -> returns False