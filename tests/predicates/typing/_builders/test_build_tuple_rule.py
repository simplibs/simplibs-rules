from typing import Tuple

from simplibs.exception import ValidationError
from simplibs.rules.containers import AllOf, Compose, ForEach
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
    """Verify tuple[str, int] constructs an AllOf with IsInstance, HasLength, and positional Compose rules."""
    rule = build_tuple_rule(tuple[str, int])

    assert isinstance(rule, AllOf)
    # IsInstance + HasLength + 2 positions
    assert len(rule.rules) == 4
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], HasLength)
    assert isinstance(rule.rules[2], Compose)
    assert isinstance(rule.rules[3], Compose)

    assert rule.is_valid(("age", 30)) is True
    assert rule.is_valid(("age", "30")) is False  # wrong type at position 1
    assert rule.is_valid(("age", 30, "extra")) is False  # wrong length (HasLength fails)


def test_build_tuple_rule_positional_failure_reports_the_failing_position() -> None:
    """Verify the failure card is the position rule's own card, not a generic 'callable' card."""
    rule = build_tuple_rule(tuple[str, int])

    exc = rule.build_exception(("age", "30"), value_name="pair")

    assert isinstance(exc, ValidationError)
    assert exc.label == "pair"
    assert exc.value == "30"  # the item at the failing position
    assert exc.expected == "instance of (int)"
