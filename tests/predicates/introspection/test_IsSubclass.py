"""Tests for the IsSubclass rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import IsSubclass


class Base:
    pass


class Derived(Base):
    pass


def test_is_subclass_contract(subtests):
    """Verify the complete contract of the IsSubclass rule."""
    rule = IsSubclass(Base)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[Derived, Base],
        invalid_values=[int, str, Derived(), "text", 123, None],
        invalid_init_params=[
            ((), {}),             # No type -> ParamError
            ((123,), {}),         # Parameter is not a type -> ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_subclass_exception_instance_input(subtests):
    """Verify diagnosis (TypeError) when instance is passed instead of a class."""
    rule = IsSubclass(Base)
    instance = Derived()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(instance, Kwargs(value_name="cls_type")),
        exception_type=ValidationError,
        label="cls_type",
        value=instance,
        error_name="IS_SUBCLASS_ERROR",
        expected="a class (subclass of (Base))",
        problem=f"Value {instance!r} is an instance of 'Derived', not a class object.",
        how_to_fix="Provide a class object itself (e.g. (Base)) instead of an instance.",
        exception=TypeError,
        verbose=False,
    )


def test_is_subclass_exception_wrong_class(subtests):
    """Verify diagnosis (TypeError) when class passed does not inherit from expected."""
    rule = IsSubclass(Base)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(int, Kwargs(value_name="cls_type")),
        exception_type=ValidationError,
        label="cls_type",
        value=int,
        error_name="IS_SUBCLASS_ERROR",
        expected="subclass of (Base)",
        problem="Class 'int' is not a subclass of (Base).",
        how_to_fix="Provide a class that inherits from (Base).",
        exception=TypeError,
        verbose=False,
    )