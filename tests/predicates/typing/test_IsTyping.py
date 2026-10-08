"""Tests for the IsTyping rule."""

from typing import Annotated, TypeVar
import pytest

# Testing tools and Kwargs wrapper
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError, ParamError

# Rules & Metadata
from simplibs.rules.predicates.comparisons import GreaterThan
from simplibs.rules.predicates.typing.IsTyping import IsTyping

T = TypeVar("T")


# ==============================================================================
# 1. MASTER CONTRACT TESTS
# ==============================================================================

def test_is_typing_contract_primitive(subtests):
    """Verify IsTyping contract for a simple primitive annotation like int."""
    rule = IsTyping(int)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 42, -100],
        invalid_values=["1", 3.14, None, [1]],
        expected_description="int",  # needs IsInstance.describe()
        rule_factory=lambda: IsTyping(int),
        deep_check=True,
        verbose=False,
    )


def test_is_typing_contract_complex_generic(subtests):
    """Verify IsTyping contract for complex composed typing constructs like list[int] | None."""
    rule = IsTyping(list[int] | None)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[[1, 2, 3], [], None],
        invalid_values=["not_a_list", [1, "2"], 123],
        expected_description="list[int] | None",  # needs IsInstance.describe()
        rule_factory=lambda: IsTyping(list[int] | None),
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST (Delegation to composed rule)
# ==============================================================================

def test_is_typing_delegates_child_exception_details(subtests):
    """Verify that IsTyping transparently delegates exception generation to the internal rule."""
    rule = IsTyping(Annotated[int, GreaterThan(0)])

    # Failure on the type (IsInstance fails for the string "abc")
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("abc", Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        expected="instance of (int)",
        verbose=False,
    )

    # Failure on the metadata rule (GreaterThan fails for the negative number -5)
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(-5, Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        expected="greater than 0",
        verbose=False,
    )


# ==============================================================================
# 3. CONSTRUCTOR & INITIALIZATION ERRORS
# ==============================================================================

def test_is_typing_invalid_annotation_raises_param_error():
    """Verify that constructing IsTyping with an unsupported annotation raises ParamError up-front."""
    # Unsupported unresolved string / forward reference
    with pytest.raises(ParamError):
        IsTyping("UnparsedForwardRef")

    # Unsupported raw TypeVar
    with pytest.raises(ParamError):
        IsTyping(T)

    # Unsupported complex type inside type[...]
    with pytest.raises(ParamError):
        IsTyping(type[list[int]])


# ==============================================================================
# 4. DESCRIPTION TEST
# ==============================================================================

def test_is_typing_describe_uses_the_annotation_spelling(subtests):
    """Verify that IsTyping describes itself with the annotation's own spelling."""

    with subtests.test("list[int]"):
        assert IsTyping(list[int]).describe() == "list[int]"

    with subtests.test("dict[str, int]"):
        assert IsTyping(dict[str, int]).describe() == "dict[str, int]"

    with subtests.test("nested generics"):
        assert IsTyping(dict[str, list[int]]).describe() == "dict[str, list[int]]"
