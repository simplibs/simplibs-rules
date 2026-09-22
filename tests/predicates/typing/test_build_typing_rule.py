from typing import Annotated, Any, Generic, NewType, TypeVar, Union

import pytest

from simplibs.exception import ParamError
from simplibs.rules.containers import AllOf, AnyOf
from simplibs.rules.predicates.comparisons import GreaterThan
from simplibs.rules.predicates.introspection import IsInstance
from simplibs.rules.predicates.typing.IsAny import IsAny
from simplibs.rules.predicates.typing.build_typing_rule import build_typing_rule


# Pomocné třídy a typy pro testování
class CustomClass:
    pass


UserId = NewType("UserId", int)
T = TypeVar("T")


def test_build_typing_rule_any() -> None:
    """Verify Any returns the IsAny singleton instance."""
    rule1 = build_typing_rule(Any)
    rule2 = build_typing_rule(Any)

    assert isinstance(rule1, IsAny)
    assert rule1 is rule2  # Ověření, že vrací identický singleton
    assert rule1.is_valid(42) is True
    assert rule1.is_valid("anything") is True
    assert rule1.is_valid(None) is True


def test_build_typing_rule_plain_class() -> None:
    """Verify plain class types return IsInstance(class)."""
    rule = build_typing_rule(int)

    assert isinstance(rule, IsInstance)
    assert rule.is_valid(42) is True
    assert rule.is_valid("42") is False

    custom_rule = build_typing_rule(CustomClass)
    assert isinstance(custom_rule, IsInstance)
    assert custom_rule.is_valid(CustomClass()) is True
    assert custom_rule.is_valid(42) is False


def test_build_typing_rule_new_type() -> None:
    """Verify NewType unwraps to its underlying supertype rule recursively."""
    rule = build_typing_rule(UserId)

    # NewType("UserId", int) se musí rozbalit na IsInstance(int)
    assert isinstance(rule, IsInstance)
    assert rule.is_valid(123) is True
    assert rule.is_valid("123") is False


def test_build_typing_rule_origin_table_dispatch() -> None:
    """Verify structured annotations route correctly through ORIGIN_TABLE builders."""
    # 1. Generic list
    list_rule = build_typing_rule(list[str])
    assert isinstance(list_rule, AllOf)
    assert list_rule.is_valid(["a", "b"]) is True
    assert list_rule.is_valid([1, 2]) is False

    # 2. Union
    union_rule = build_typing_rule(Union[int, str])
    assert isinstance(union_rule, AnyOf)
    assert union_rule.is_valid(10) is True
    assert union_rule.is_valid("10") is True
    assert union_rule.is_valid(10.5) is False

    # 3. Annotated
    annotated_rule = build_typing_rule(Annotated[int, GreaterThan(0)])
    assert isinstance(annotated_rule, AllOf)
    assert annotated_rule.is_valid(5) is True
    assert annotated_rule.is_valid(-5) is False


def test_build_typing_rule_unsupported_non_type_raises() -> None:
    """Verify raw TypeVar or unprocessable constructs raise ParamError."""
    with pytest.raises(ParamError):
        build_typing_rule(T)

    with pytest.raises(ParamError):
        build_typing_rule("UnparsedForwardRef")  # Prostý string bez typu


def test_build_typing_rule_unsupported_origin_raises() -> None:
    """Verify unsupported origin generic constructs raise ParamError."""
    # Vytvoříme generic s originem, který NENÍ v ORIGIN_TABLE
    class UnknownGeneric(Generic[T]):
        pass

    with pytest.raises(ParamError):
        build_typing_rule(UnknownGeneric[int])