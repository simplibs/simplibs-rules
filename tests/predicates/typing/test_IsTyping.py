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

    # Selhání na typu (IsInstance selže u řetězce "abc")
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("abc", Kwargs(value_name="count")),
        exception_type=ValidationError,
        label="count",
        expected="instance of (int)",
        verbose=False,
    )

    # Selhání na metadatovém pravidlu (GreaterThan selže u záporného čísla -5)
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
    # Nepodporovaný nevyluštěný string / forward reference
    with pytest.raises(ParamError):
        IsTyping("UnparsedForwardRef")

    # Nepodporovaný raw TypeVar
    with pytest.raises(ParamError):
        IsTyping(T)

    # Nepodporovaný složitý typ uvnitř type[...]
    with pytest.raises(ParamError):
        IsTyping(type[list[int]])