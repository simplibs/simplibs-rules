from typing import Annotated

from simplibs.rules.containers import AllOf, Compose
from simplibs.rules.predicates.comparisons import GreaterThan
from simplibs.rules.predicates.introspection import IsInstance
from simplibs.rules.predicates.typing._builders.build_annotated_rule import (
    build_annotated_rule,
)


def test_build_annotated_rule_with_rule_metadata() -> None:
    """Verify Annotated[int, GreaterThan(0)] combines type check and Rule metadata into AllOf."""
    rule = build_annotated_rule(Annotated[int, GreaterThan(0)])

    # 1. Strukturní kontrola (To hlavné, co builder dělá)
    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], GreaterThan)

    # 2. Rychlá funkční prověrka (bez křehkého assert_rule_contract)
    assert rule.is_valid(1) is True
    assert rule.is_valid(100) is True
    assert rule.is_valid(0) is False
    assert rule.is_valid(-10) is False
    assert rule.is_valid("5") is False


def test_build_annotated_rule_with_callable_and_ignored_metadata() -> None:
    """Verify plain callables are wrapped via Compose and non-predicate metadata is ignored."""
    is_even = lambda x: x % 2 == 0
    # "some description" by mělo být ignorováno
    rule = build_annotated_rule(Annotated[int, is_even, "some description"])

    # 1. Strukturní kontrola
    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], Compose)

    # 2. Rychlá funkční prověrka
    assert rule.is_valid(2) is True
    assert rule.is_valid(4) is True
    assert rule.is_valid(1) is False
    assert rule.is_valid("2") is False


def test_build_annotated_rule_without_custom_metadata() -> None:
    """Verify Annotated[int, "only string doc"] unwraps to just IsInstance(int)."""
    # Pokud v metadata není žádné Rule ani callable, nemá vzniknout AllOf!
    rule = build_annotated_rule(Annotated[int, "just docstring"])

    # Má vrátit přímo IsInstance, ne AllOf
    assert isinstance(rule, IsInstance)
    assert rule.is_valid(42) is True
    assert rule.is_valid("42") is False