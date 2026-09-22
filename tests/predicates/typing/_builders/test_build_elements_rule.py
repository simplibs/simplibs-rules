from typing import Iterable, List

from simplibs.rules.containers import AllOf, ForEach
from simplibs.rules.predicates.introspection import IsInstance
from simplibs.rules.predicates.typing._builders.build_elements_rule import (
    build_elements_rule,
)


def test_build_elements_rule_subscripted() -> None:
    """Verify list[int] generates AllOf(IsInstance(list), ForEach(IsInstance(int)))."""
    rule = build_elements_rule(list[int])

    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], ForEach)

    assert rule.is_valid([1, 2, 3]) is True
    assert rule.is_valid([]) is True
    assert rule.is_valid([1, "2", 3]) is False
    assert rule.is_valid("1, 2, 3") is False


def test_build_elements_rule_unsubscripted() -> None:
    """Verify unsubscripted generic origin (e.g. typing.List) generates IsInstance without ForEach."""
    rule = build_elements_rule(List)

    assert isinstance(rule, IsInstance)
    assert rule.is_valid([1, "anything", True]) is True
    assert rule.is_valid((1, 2)) is False


def test_build_elements_rule_with_container_override() -> None:
    """Verify container_type override forces a specific IsInstance type."""
    rule = build_elements_rule(Iterable[str], container_type=list)

    assert isinstance(rule, AllOf)
    # První pravidlo musí být IsInstance(list), nikoli IsInstance(Iterable)
    assert isinstance(rule.rules[0], IsInstance)
    assert rule.is_valid(["a", "b"]) is True
    assert rule.is_valid(("a", "b")) is False  # tuple selže na IsInstance(list)