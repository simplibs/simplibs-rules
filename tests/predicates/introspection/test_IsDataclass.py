"""Tests for the IsDataclass rule."""

import dataclasses
from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import IsDataclass


@dataclasses.dataclass
class SampleDataclass:
    name: str


class RegularClass:
    pass


def test_is_dataclass_contract(subtests):
    """Verify the complete contract of the IsDataclass rule."""
    rule = IsDataclass()
    instance = SampleDataclass(name="test")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[instance, SampleDataclass],
        invalid_values=[RegularClass(), RegularClass, "text", 123, None, [1, 2]],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_dataclass_exception(subtests):
    """Verify diagnosis (TypeError) when value is not a dataclass."""
    rule = IsDataclass()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="config")),
        exception_type=ValidationError,
        label="config",
        value=123,
        error_name="IS_DATACLASS_ERROR",
        expected="dataclass instance or type",
        problem="Value 123 of type 'int' is not a dataclass.",
        how_to_fix="Provide an instance of, or a class decorated with, @dataclass.",
        exception=TypeError,
        verbose=False,
    )