"""Tests for the IsType rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import IsType


class DummyClass:
    pass


def test_is_type_contract(subtests):
    """Verify the complete contract of the IsType rule."""
    rule = IsType()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[int, str, object, DummyClass, type],
        invalid_values=[123, "text", DummyClass(), None, [1, 2]],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_type_exception(subtests):
    """Verify diagnosis (TypeError) when value is not a type/class."""
    rule = IsType()
    instance = DummyClass()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(instance, Kwargs(value_name="target_cls")),
        exception_type=ValidationError,
        label="target_cls",
        value=instance,
        error_name="IS_TYPE_ERROR",
        expected="a class (type object)",
        problem=f"Value {instance!r} is an instance of 'DummyClass', not a class object itself.",
        how_to_fix="Provide a class object (type), not an instance.",
        exception=TypeError,
        verbose=False,
    )