from typing import Tuple

from simplibs.rules.containers import AllOf, ForEach
from simplibs.rules.predicates.introspection import HasLength, IsInstance
from simplibs.rules.predicates.typing._builders.build_tuple_rule import (
    build_tuple_rule,
)


def test_build_tuple_rule_homogeneous() -> None:
    """Verify tuple[int, ...] delegates to build_elements_rule (AllOf with ForEach)."""
    rule = build_tuple_rule(tuple[int, ...])

    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], ForEach)

    assert rule.is_valid((1, 2, 3, 4)) is True
    assert rule.is_valid(()) is True
    assert rule.is_valid((1, "2")) is False


def test_build_tuple_rule_unsubscripted() -> None:
    """Verify bare tuple delegates to elements rule returning IsInstance(tuple)."""
    rule = build_tuple_rule(tuple)

    assert isinstance(rule, IsInstance)
    assert rule.is_valid((1, "a", True)) is True
    assert rule.is_valid([1, 2]) is False


def test_build_tuple_rule_positional() -> None:
    """Verify tuple[str, int] constructs an AllOf with IsInstance, HasLength, and positional closures."""
    rule = build_tuple_rule(tuple[str, int])

    assert isinstance(rule, AllOf)
    # IsInstance + HasLength + 2 pozice
    assert len(rule.rules) == 4
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], HasLength)

    assert rule.is_valid(("age", 30)) is True
    assert rule.is_valid(("age", "30")) is False  # špatný typ na pozici 1
    assert rule.is_valid(("age", 30, "extra")) is False  # špatná délka (HasLength selže)