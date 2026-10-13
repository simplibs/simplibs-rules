import pytest
import typing
from typing import Annotated, Any, Callable, Generic, Literal, NewType, TypeVar, Union
from collections.abc import Collection, Iterable, Sequence

from simplibs.exception import ParamError, ValidationError
from simplibs.rules.containers import AllOf, AnyOf, Described
from simplibs.rules.predicates.comparisons import GreaterThan
from simplibs.rules.predicates.introspection import IsInstance, IsReiterable
from simplibs.rules.predicates.typing.IsAny import IsAny
from simplibs.rules.predicates.typing.build_typing_rule import build_typing_rule


# Helper classes and types for testing
class CustomClass:
    pass


UserId = NewType("UserId", int)
T = TypeVar("T")


def test_build_typing_rule_any() -> None:
    """Verify Any returns the IsAny singleton instance."""
    rule1 = build_typing_rule(Any)
    rule2 = build_typing_rule(Any)

    assert isinstance(rule1, IsAny)
    assert rule1 is rule2  # Verify that the identical singleton is returned
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

    # NewType("UserId", int) must unwrap to IsInstance(int)
    assert isinstance(rule, IsInstance)
    assert rule.is_valid(123) is True
    assert rule.is_valid("123") is False


def test_build_typing_rule_origin_table_dispatch() -> None:
    """Verify structured annotations route correctly through ORIGIN_TABLE builders."""
    # 1. Generic list
    list_rule = build_typing_rule(list[str])
    assert isinstance(list_rule, Described)
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
        build_typing_rule("UnparsedForwardRef")  # Plain string, not a type


def test_build_typing_rule_unsupported_origin_raises() -> None:
    """Verify unsupported origin generic constructs raise ParamError."""
    # Create a generic whose origin is NOT in ORIGIN_TABLE
    class UnknownGeneric(Generic[T]):
        pass

    with pytest.raises(ParamError):
        build_typing_rule(UnknownGeneric[int])


def test_build_typing_rule_wraps_generics_in_described(subtests) -> None:
    """Verify generic constructs describe themselves with the annotation's own spelling."""
    expected_texts = {
        list[int]: "list[int]",
        set[str]: "set[str]",
        dict[str, int]: "dict[str, int]",
        tuple[str, int]: "tuple[str, int]",
        tuple[int, ...]: "tuple[int, ...]",
        list[str | int]: "list[str | int]",
        list[list[int]]: "list[list[int]]",
        Literal["a", "b"]: "Literal['a', 'b']",
        Callable[[int], str]: "Callable[[int], str]",
        type[int]: "type[int]",
        Iterable[int]: "Iterable[int]",
        typing.Iterable[int]: "Iterable[int]",

    }

    for annotation, text in expected_texts.items():
        with subtests.test(text):
            rule = build_typing_rule(annotation)
            assert isinstance(rule, Described)
            assert rule.describe() == text


def test_build_typing_rule_does_not_wrap_union_and_annotated(subtests) -> None:
    """Verify Union and Annotated keep composing their own description."""

    with subtests.test("Union"):
        rule = build_typing_rule(Union[int, str])
        assert isinstance(rule, AnyOf)
        assert not isinstance(rule, Described)

    with subtests.test("Annotated"):
        rule = build_typing_rule(Annotated[int, GreaterThan(0)])
        assert isinstance(rule, AllOf)
        assert not isinstance(rule, Described)


def test_build_typing_rule_does_not_wrap_primitives(subtests) -> None:
    """Verify plain classes, bare generics and Rule instances are returned as built, without a wrapper."""

    with subtests.test("plain class"):
        assert isinstance(build_typing_rule(int), IsInstance)

    with subtests.test("bare generic"):
        assert isinstance(build_typing_rule(list), IsInstance)

    with subtests.test("Rule instance passes through unchanged"):
        rule = GreaterThan(0)
        assert build_typing_rule(rule) is rule


def test_build_typing_rule_described_rule_behaves_like_the_decomposition() -> None:
    """Verify the Described wrapper changes the text only, not the validation result."""
    rule = build_typing_rule(dict[str, list[int]])

    assert rule.is_valid({"a": [1, 2]}) is True
    assert rule.is_valid({"a": [1, "2"]}) is False
    assert rule.is_valid({1: [1]}) is False
    assert rule.is_valid([1]) is False


def test_build_typing_rule_describe_of_union_members() -> None:
    """Verify a Union describes its members (needs IsInstance.describe(), see the introspection batch)."""
    assert build_typing_rule(int | None).describe() == "int | None"
    assert build_typing_rule(list[int] | set[int] | str).describe() == "list[int] | set[int] | str"


def _generator(*items):
    yield from items


def test_build_typing_rule_iterable_accepts_reiterable_containers(subtests) -> None:
    """Verify Iterable[int] still validates re-iterable containers by their items."""
    rule = build_typing_rule(Iterable[int])

    for value in ([1, 2], (1, 2), {1, 2}, frozenset({1}), range(3), {1: "a"}.keys(), []):
        with subtests.test(repr(value)):
            assert rule.is_valid(value) is True

    for value in ([1, "2"], "abc", 123, None):
        with subtests.test(repr(value)):
            assert rule.is_valid(value) is False


def test_build_typing_rule_iterable_rejects_one_shot_iterators(subtests) -> None:
    """Verify generators and other iterators are rejected, for both spellings of Iterable."""
    for annotation in (Iterable[int], typing.Iterable[int]):
        rule = build_typing_rule(annotation)

        for factory in (lambda: _generator(1, 2), lambda: iter([1, 2]), lambda: map(int, "12")):
            with subtests.test(f"{annotation} {factory()!r}"):
                assert rule.is_valid(factory()) is False


def test_build_typing_rule_iterable_does_not_consume_a_rejected_iterator() -> None:
    """Verify the rejected generator reaches the caller untouched (the original silent-data-loss bug)."""
    rule = build_typing_rule(Iterable[int])
    generator = _generator(1, 2, 3)

    assert rule.is_valid(generator) is False
    assert list(generator) == [1, 2, 3]


def test_build_typing_rule_iterable_failure_card_names_the_iterator() -> None:
    """Verify the failure card is the IsReiterable one, even when the iterator holds bad items."""
    rule = build_typing_rule(Iterable[int])
    generator = _generator(1, "a", 3)

    exc = rule.build_exception(generator, "items")

    assert isinstance(exc, ValidationError)
    assert exc.error_name == "IS_REITERABLE_ERROR"
    assert exc.exception is TypeError
    assert list(generator) == [1, "a", 3]


def test_build_typing_rule_bare_iterable_still_accepts_iterators(subtests) -> None:
    """Verify bare Iterable (no item type) is the way to accept a generator, and leaves it untouched."""
    for annotation in (Iterable, typing.Iterable):
        with subtests.test(repr(annotation)):
            rule = build_typing_rule(annotation)
            generator = _generator(1, 2)

            assert rule.is_valid(generator) is True
            assert list(generator) == [1, 2]
            assert rule.is_valid(123) is False


def test_build_typing_rule_sequence_and_collection_reject_iterators_by_type(subtests) -> None:
    """Verify Sequence[T]/Collection[T] reject generators on their own (no extra guard needed)."""
    for annotation in (Sequence[int], Collection[int]):
        with subtests.test(repr(annotation)):
            rule = build_typing_rule(annotation)
            generator = _generator(1, 2)

            assert rule.is_valid(generator) is False
            assert list(generator) == [1, 2]
            assert rule.is_valid([1, 2]) is True


def test_build_typing_rule_nested_iterable_guard_applies_at_every_level() -> None:
    """Verify nested Iterable[T] slots reject iterators too, without consuming them."""
    rule = build_typing_rule(list[Iterable[int]])
    inner = _generator(1, 2)

    assert rule.is_valid([[1, 2], (3,)]) is True
    assert rule.is_valid([inner]) is False
    assert list(inner) == [1, 2]


def test_build_typing_rule_optional_iterable() -> None:
    """Verify Iterable[int] | None keeps the guard inside the Union."""
    rule = build_typing_rule(Iterable[int] | None)

    assert rule.is_valid(None) is True
    assert rule.is_valid([1, 2]) is True
    assert rule.is_valid(_generator(1, 2)) is False
    assert rule.describe() == "Iterable[int] | None"