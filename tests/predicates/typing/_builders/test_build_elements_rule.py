import collections.abc
import typing
from typing import Iterable, List

import pytest

from simplibs.exception import ValidationError
from simplibs.rules.containers import AllOf, ForEach
from simplibs.rules.predicates.introspection import IsInstance, IsReiterable
from simplibs.rules.predicates.typing._builders.build_elements_rule import (
    build_elements_rule,
)


def _generator(*items):
    yield from items


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
    # The first rule must be IsInstance(list), not IsInstance(Iterable)
    assert isinstance(rule.rules[0], IsInstance)
    assert rule.is_valid(["a", "b"]) is True
    assert rule.is_valid(("a", "b")) is False  # a tuple fails on IsInstance(list)
    # With an explicit container no Iterable guard is added
    assert len(rule.rules) == 2


# ==============================================================================
# Iterable[T] — one-shot iterators are rejected before ForEach could consume them
# ==============================================================================

@pytest.mark.parametrize("annotation", [typing.Iterable[int], collections.abc.Iterable[int]])
def test_build_elements_rule_iterable_has_reiterable_guard(annotation) -> None:
    """Verify Iterable[T] is IsInstance -> IsReiterable -> ForEach, in this order."""
    rule = build_elements_rule(annotation)

    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 3
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], IsReiterable)
    assert isinstance(rule.rules[2], ForEach)


@pytest.mark.parametrize(
    "annotation",
    [
        list[int],
        set[int],
        frozenset[int],
        collections.abc.Sequence[int],
        collections.abc.Collection[int],
        typing.Sequence[int],
        typing.Collection[int],
    ],
)
def test_build_elements_rule_other_containers_have_no_guard(annotation) -> None:
    """Verify only Iterable[T] gets the guard — the others can never be iterators."""
    rule = build_elements_rule(annotation)

    assert len(rule.rules) == 2
    assert not any(isinstance(part, IsReiterable) for part in rule.rules)


def test_build_elements_rule_homogeneous_tuple_has_no_guard() -> None:
    """Verify tuple[T, ...] routed with container_type=tuple has no guard."""
    rule = build_elements_rule(tuple[int, ...], container_type=tuple)

    assert len(rule.rules) == 2
    assert not any(isinstance(part, IsReiterable) for part in rule.rules)


def test_build_elements_rule_iterable_accepts_reiterable_containers() -> None:
    """Verify containers that can be walked repeatedly still validate by their items."""
    rule = build_elements_rule(Iterable[int])

    assert rule.is_valid([1, 2]) is True
    assert rule.is_valid((1, 2)) is True
    assert rule.is_valid({1, 2}) is True
    assert rule.is_valid(range(3)) is True
    assert rule.is_valid({1: "a"}.keys()) is True
    assert rule.is_valid([]) is True

    assert rule.is_valid([1, "2"]) is False
    assert rule.is_valid(123) is False
    assert rule.is_valid(None) is False


def test_build_elements_rule_iterable_rejects_iterators_without_consuming_them() -> None:
    """Verify a generator is rejected and arrives untouched."""
    rule = build_elements_rule(Iterable[int])

    generator = _generator(1, 2, 3)
    assert rule.is_valid(generator) is False
    assert list(generator) == [1, 2, 3]

    iterator = iter([1, 2, 3])
    assert rule.is_valid(iterator) is False
    assert list(iterator) == [1, 2, 3]


def test_build_elements_rule_iterable_card_names_the_iterator_problem() -> None:
    """Verify an iterator with bad items reports the iterator, not an internal 'unreachable' error."""
    rule = build_elements_rule(Iterable[int])

    generator = _generator(1, "a", 3)
    exc = rule.build_exception(generator, "items")

    assert isinstance(exc, ValidationError)
    assert exc.error_name == "IS_REITERABLE_ERROR"
    assert exc.exception is TypeError
    assert list(generator) == [1, "a", 3]  # still untouched


def test_build_elements_rule_bare_iterable_accepts_iterators_untouched() -> None:
    """Verify bare typing.Iterable has no item check, so an iterator passes through unconsumed."""
    rule = build_elements_rule(typing.Iterable)

    assert isinstance(rule, IsInstance)

    generator = _generator(1, 2)
    assert rule.is_valid(generator) is True
    assert list(generator) == [1, 2]
    assert rule.is_valid(123) is False
