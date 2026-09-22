from typing import Any, Type, Union

import pytest

from simplibs.exception import ParamError
from simplibs.rules.containers import AllOf, AnyOf
from simplibs.rules.predicates.introspection import IsSubclass, IsType
from simplibs.rules.predicates.typing._builders.build_type_rule import build_type_rule


class Base:
    pass


class Derived(Base):
    pass


class Other:
    pass


def test_build_type_rule_bare() -> None:
    """Verify bare Type/type returns pure IsType rule."""
    rule = build_type_rule(Type)

    assert isinstance(rule, IsType)
    assert rule.is_valid(Base) is True
    assert rule.is_valid(int) is True
    assert rule.is_valid(Base()) is False


def test_build_type_rule_any_base() -> None:
    """Verify type[Any] behaves like bare type/Type and returns pure IsType rule."""
    rule = build_type_rule(type[Any])

    assert isinstance(rule, IsType)
    assert rule.is_valid(Base) is True
    assert rule.is_valid(int) is True
    assert rule.is_valid(Base()) is False


def test_build_type_rule_single_class() -> None:
    """Verify type[Base] creates AllOf(IsType, IsSubclass(Base))."""
    rule = build_type_rule(type[Base])

    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], IsType)
    assert isinstance(rule.rules[1], IsSubclass)

    assert rule.is_valid(Base) is True
    assert rule.is_valid(Derived) is True
    assert rule.is_valid(Other) is False


def test_build_type_rule_union_base() -> None:
    """Verify type[Base | Other] creates AllOf(IsType, AnyOf(IsSubclass(Base), IsSubclass(Other)))."""
    rule = build_type_rule(type[Union[Base, Other]])

    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], IsType)
    assert isinstance(rule.rules[1], AnyOf)

    assert rule.is_valid(Base) is True
    assert rule.is_valid(Other) is True
    assert rule.is_valid(int) is False


def test_build_type_rule_unsupported_base_raises() -> None:
    """Verify unsupported type parameters (like generic list[int]) raise ParamError."""
    with pytest.raises(ParamError):
        build_type_rule(type[list[int]])