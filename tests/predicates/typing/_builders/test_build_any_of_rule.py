from typing import Optional, Union

from simplibs.rules.containers import AnyOf
from simplibs.rules.predicates.introspection import IsInstance
from simplibs.rules.predicates.typing._builders.build_any_of_rule import (
    build_any_of_rule,
)


def test_build_any_of_rule_with_union() -> None:
    """Verify Union[int, str] produces an AnyOf container with respective IsInstance rules."""
    rule = build_any_of_rule(Union[int, str])

    assert isinstance(rule, AnyOf)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], IsInstance)

    assert rule.is_valid(42) is True
    assert rule.is_valid("hello") is True
    assert rule.is_valid(3.14) is False


def test_build_any_of_rule_with_pipe_operator() -> None:
    """Verify `int | float` produces AnyOf with IsInstance checks."""
    rule = build_any_of_rule(int | float)

    assert isinstance(rule, AnyOf)
    assert len(rule.rules) == 2

    assert rule.is_valid(10) is True
    assert rule.is_valid(2.5) is True
    assert rule.is_valid("10") is False


def test_build_any_of_rule_with_optional() -> None:
    """Verify Optional[int] (which is Union[int, NoneType]) accepts int and None."""
    rule = build_any_of_rule(Optional[int])

    assert isinstance(rule, AnyOf)
    assert len(rule.rules) == 2

    assert rule.is_valid(100) is True
    assert rule.is_valid(None) is True
    assert rule.is_valid("none") is False