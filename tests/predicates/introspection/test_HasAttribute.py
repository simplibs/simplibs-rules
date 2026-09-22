"""Tests for the HasAttribute rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import HasAttribute


class DummyObject:
    """Helper object for testing attribute presence."""

    def __init__(self) -> None:
        self.existing_attr = 42

    def method(self) -> None:
        pass

    @property
    def dynamic_missing_property(self) -> None:
        raise AttributeError("Property is dynamically unavailable")


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_has_attribute_contract(subtests):
    """Verify the complete contract of the HasAttribute rule."""
    rule = HasAttribute("existing_attr")
    dummy = DummyObject()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[dummy],
        invalid_values=["string_object", 123, None, [1, 2, 3]],
        invalid_init_params=[
            ((123,), {}),     # attr_name parameter must be str -> ParamError
            ((None,), {}),    # attr_name parameter must not be None -> ParamError
            (([],), {}),      # attr_name parameter must not be list -> ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_has_attribute_exception(subtests):
    """Verify diagnosis (AttributeError) when object lacks the required attribute."""
    rule = HasAttribute("missing_feature")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="target")),
        exception_type=ValidationError,
        label="target",
        value=123,
        error_name="ATTRIBUTE_ERROR",
        expected="object with attribute 'missing_feature'",
        problem="Object of type 'int' does not have attribute 'missing_feature'.",
        how_to_fix="Provide an object that supports the 'missing_feature' attribute or method.",
        exception=AttributeError,
        verbose=False,
    )


# ==============================================================================
# 3. SPECIFIC EDGE CASES
# ==============================================================================

def test_has_attribute_edge_cases():
    """Verify behavior on methods, built-in types, and dynamic attributes."""
    dummy = DummyObject()

    # Method and built-in attributes
    assert HasAttribute("method").is_valid(dummy) is True
    assert HasAttribute("append").is_valid([]) is True
    assert HasAttribute("lower").is_valid("hello") is True

    # Non-existent attribute on object
    assert HasAttribute("missing_attr").is_valid(dummy) is False

    # Property raising AttributeError (hasattr catches it and returns False)
    assert HasAttribute("dynamic_missing_property").is_valid(dummy) is False