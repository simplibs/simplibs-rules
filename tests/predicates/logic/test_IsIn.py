"""Tests for the IsIn rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.logic import IsIn


def test_is_in_contract(subtests):
    """Verify the complete contract of the IsIn rule (non-strict mode)."""
    options = [1, 2, "admin", None]
    rule = IsIn(options)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 2, "admin", None],
        invalid_values=[3, "user", [1]],  # [1] triggers unhashable fallback/invalid test
        invalid_init_params=[
            ((123,), {}),       # Scalar is not a container -> ParamError
            (("string",), {}),  # String is not an allowed container -> ParamError
            ((None,), {}),      # None is not a container -> ParamError
        ],
        deep_check=True,
        verbose=False,
    )


def test_is_in_strict_mode(subtests):
    """Verify strict type enforcement for bool vs int distinction."""
    options = [1, 0]

    non_strict_rule = IsIn(options, strict=False)
    strict_rule = IsIn(options, strict=True)

    with subtests.test("Non-strict allows True for 1 and False for 0"):
        assert non_strict_rule.is_valid(1) is True
        assert non_strict_rule.is_valid(True) is True
        assert non_strict_rule.is_valid(0) is True
        assert non_strict_rule.is_valid(False) is True

    with subtests.test("Strict mode rejects True for 1 and False for 0"):
        assert strict_rule.is_valid(1) is True
        assert strict_rule.is_valid(0) is True
        assert strict_rule.is_valid(True) is False
        assert strict_rule.is_valid(False) is False

    with subtests.test("Strict mode works for bool option containers"):
        bool_strict_rule = IsIn([True], strict=True)
        assert bool_strict_rule.is_valid(True) is True
        assert bool_strict_rule.is_valid(1) is False


def test_is_in_exception_value_missing(subtests):
    """Verify diagnosis (ValueError) when value is missing from collection."""
    options = ["draft", "published"]
    rule = IsIn(options)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("archived", Kwargs(value_name="status")),
        exception_type=ValidationError,
        label="status",
        value="archived",
        error_name="IS_IN_ERROR",
        expected="one of ['draft', 'published']",
        problem="Value 'archived' is not one of ['draft', 'published'].",
        how_to_fix="Provide a value contained in ['draft', 'published'].",
        exception=ValueError,
        verbose=False,
    )


def test_is_in_exception_unhashable_value(subtests):
    """Verify diagnosis (TypeError) when value is unhashable against a set."""
    options = {1, 2, 3}
    rule = IsIn(options)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([1, 2], Kwargs(value_name="payload")),
        exception_type=ValidationError,
        label="payload",
        value=[1, 2],
        error_name="IS_IN_ERROR",
        expected="one of {1, 2, 3}",
        problem="Value [1, 2] of type 'list' cannot be looked up in container 'set'.",
        how_to_fix="Provide a hashable value (e.g. tuple instead of list) or a compatible container.",
        exception=TypeError,
        verbose=False,
    )


def test_is_in_large_container_truncation(subtests):
    """Verify representation truncation for large containers (>60 characters)."""
    large_list = list(range(100))
    rule = IsIn(large_list)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(999, Kwargs(value_name="id")),
        exception_type=ValidationError,
        label="id",
        value=999,
        error_name="IS_IN_ERROR",
        expected="one of list(size=100)",
        problem="Value 999 is not one of list(size=100).",
        how_to_fix="Provide a value contained in list(size=100).",
        exception=ValueError,
        verbose=False,
    )