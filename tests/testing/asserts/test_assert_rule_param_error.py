"""Tests for the assert_rule_param_error function."""

from typing import Any
import pytest
from _pytest.outcomes import Failed

from simplibs.exception import ParamError
from simplibs.rules.testing.asserts.assert_rule_param_error import (
    assert_rule_param_error,
)


# --- Mock Factory Functions for Testing ---

def dummy_rule_factory_correct(min_val: int, max_val: int = 10) -> None:
    """Constructor that raises ParamError for invalid arguments."""
    if not isinstance(min_val, int):
        raise ParamError("min_val must be an integer")
    if min_val > max_val:
        raise ParamError("min_val cannot be greater than max_val")


def dummy_rule_factory_wrong_exception(min_val: int) -> None:
    """Constructor that raises TypeError instead of ParamError."""
    if not isinstance(min_val, int):
        raise TypeError("Invalid type")


def dummy_rule_factory_no_raise(min_val: int) -> None:
    """Constructor that raises no exception even for invalid inputs."""
    pass


# --- Tests ---

def test_assert_rule_param_error_success(subtests):
    """Verify that a constructor error raising ParamError passes correctly."""
    invalid_params = [
        (("not_an_int",), {}),          # Invalid type passed via positional arg
        ((15,), {"max_val": 10}),       # Invalid range passed via kwarg
    ]
    assert_rule_param_error(
        subtests,
        rule_factory=dummy_rule_factory_correct,
        invalid_init_params=invalid_params,
    )


def test_assert_rule_param_error_fails_on_wrong_exception_type(subtests):
    """Verify failure when constructor raises an exception type other than ParamError."""
    invalid_params = [
        (("not_an_int",), {}),
    ]
    with pytest.raises((AssertionError, Failed)):
        assert_rule_param_error(
            subtests,
            rule_factory=dummy_rule_factory_wrong_exception,
            invalid_init_params=invalid_params,
            verbose=False,
        )


def test_assert_rule_param_error_fails_when_no_exception_raised(subtests):
    """Verify failure when constructor raises no exception for invalid inputs."""
    invalid_params = [
        (("invalid_val",), {}),
    ]
    with pytest.raises((AssertionError, Failed)):
        assert_rule_param_error(
            subtests,
            rule_factory=dummy_rule_factory_no_raise,
            invalid_init_params=invalid_params,
            verbose=False,
        )