from typing import Dict, Mapping

from simplibs.rules.containers import AllOf, Compose, ForEach
from simplibs.rules.predicates.introspection import IsInstance
from simplibs.rules.predicates.typing._builders.build_key_value_rule import (
    build_key_value_rule,
)


def test_build_key_value_rule_subscripted() -> None:
    """Verify dict[str, int] constructs IsInstance, Compose for keys, and Compose for values."""
    rule = build_key_value_rule(dict[str, int])

    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 3
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], Compose)
    assert isinstance(rule.rules[2], Compose)

    assert rule.is_valid({"a": 1, "b": 2}) is True
    assert rule.is_valid({}) is True
    assert rule.is_valid({1: 1}) is False  # špatný klíč
    assert rule.is_valid({"a": "1"}) is False  # špatná hodnota
    assert rule.is_valid([("a", 1)]) is False  # není dict


def test_build_key_value_rule_unsubscripted() -> None:
    """Verify bare dict produces only an IsInstance(dict) rule."""
    rule = build_key_value_rule(Dict)

    assert isinstance(rule, IsInstance)
    assert rule.is_valid({"any": 123, 456: "thing"}) is True
    assert rule.is_valid("not_a_dict") is False