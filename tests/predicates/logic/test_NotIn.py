"""Tests for the NotIn rule."""

from typing import Any
import pytest

from simplibs.exception.testing import (
    assert_exception_function,
    assert_exception_fields,
    Kwargs,
)
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.logic import NotIn


def test_not_in_contract(subtests):
    """Verify the complete contract of the NotIn rule (non-strict mode)."""
    forbidden = ["banned", "suspended"]
    rule = NotIn(forbidden)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["active", "pending", 123, None],
        invalid_values=["banned", "suspended"],
        invalid_init_params=[
            ((123,), {}),       # Scalar is not a container -> ParamError
            (("string",), {}),  # String is not an allowed container -> ParamError
            ((None,), {}),      # None is not a container -> ParamError
        ],
        deep_check=True,
        verbose=False,
    )


def test_not_in_strict_mode(subtests):
    """Verify strict type enforcement for bool vs int distinction in negative checks."""
    forbidden = [1, 0]

    non_strict_rule = NotIn(forbidden, strict=False)
    strict_rule = NotIn(forbidden, strict=True)

    with subtests.test("Non-strict rejects True for 1 and False for 0"):
        assert non_strict_rule.is_valid(1) is False
        assert non_strict_rule.is_valid(True) is False
        assert non_strict_rule.is_valid(0) is False
        assert non_strict_rule.is_valid(False) is False

    with subtests.test("Strict mode allows True when 1 is forbidden and False when 0 is forbidden"):
        assert strict_rule.is_valid(1) is False
        assert strict_rule.is_valid(0) is False
        assert strict_rule.is_valid(True) is True
        assert strict_rule.is_valid(False) is True

    with subtests.test("Strict mode rejects True when True is explicitly forbidden"):
        bool_strict_rule = NotIn([True], strict=True)
        assert bool_strict_rule.is_valid(True) is False
        assert bool_strict_rule.is_valid(1) is True


def test_not_in_exception_value_present(subtests):
    """Verify diagnosis (ValueError) when value is found in forbidden collection."""
    forbidden = ["admin", "root"]
    rule = NotIn(forbidden)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("admin", Kwargs(value_name="username")),
        exception_type=ValidationError,
        label="username",
        value="admin",
        error_name="NOT_IN_ERROR",
        expected="value not in ['admin', 'root']",
        problem="Value 'admin' is forbidden — it appears in ['admin', 'root'].",
        how_to_fix="Provide a value that is not present in ['admin', 'root'].",
        exception=ValueError,
        verbose=False,
    )


def test_not_in_unhashable_value_is_valid():
    """Verify that an unhashable value passes as valid for NotIn (cannot be present in set)."""
    rule = NotIn({1, 2, 3})
    assert rule.is_valid([1, 2]) is True


def test_not_in_exception_unhashable_value(subtests):
    """Verify diagnosis (TypeError) directly from build_exception for unhashable value in a set."""
    rule = NotIn({1, 2, 3})

    # Manually build exception from the rule
    exc = rule.build_exception([1, 2], value_name="item")

    # Verify exception fields generated via assert_exception_fields
    assert_exception_fields(
        subtests,
        exc=exc,
        label="item",
        value=[1, 2],
        error_name="NOT_IN_ERROR",
        expected="value not in {1, 2, 3}",
        problem="Value [1, 2] of type 'list' cannot be checked against container 'set'.",
        how_to_fix="Provide a hashable value or a compatible container.",
        exception=TypeError,
    )