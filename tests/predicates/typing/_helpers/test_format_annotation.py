"""Tests for the format_annotation helper."""

import typing
from collections import abc as collections_abc
from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Mapping,
    NewType,
    Optional,
    Tuple,
    Type,
    Union,
)

from simplibs.rules.base_class import Rule
from simplibs.rules.predicates.typing._helpers.format_annotation import format_annotation

UserId = NewType("UserId", int)


class CustomClass:
    pass


class DummyRule(Rule):
    """Rule with its own description, usable as an annotation or as Annotated metadata."""

    __slots__ = ()

    def is_valid(self, value: Any) -> bool:
        return True

    def build_exception(self, value: Any, value_name: str | None = None, context: str | None = None):
        return ValueError("Error")

    def describe(self) -> str:
        return "> 0"


def is_even(value: Any) -> bool:
    return value % 2 == 0


def test_format_annotation_constants_and_plain_classes(subtests) -> None:
    """Verify Any, None, Ellipsis, plain classes and NewType."""
    cases = {
        "Any": (Any, "Any"),
        "None": (None, "None"),
        "NoneType": (type(None), "None"),
        "Ellipsis": (Ellipsis, "..."),
        "builtin class": (int, "int"),
        "custom class": (CustomClass, "CustomClass"),
        "NewType": (UserId, "UserId"),
    }

    for label, (annotation, text) in cases.items():
        with subtests.test(label):
            assert format_annotation(annotation) == text


def test_format_annotation_generics(subtests) -> None:
    """Verify subscripted generics, including legacy typing aliases and nesting."""
    cases = {
        "list": (list[int], "list[int]"),
        "typing.List": (List[int], "list[int]"),
        "dict": (dict[str, int], "dict[str, int]"),
        "typing.Dict": (Dict[str, int], "dict[str, int]"),
        "typing.Mapping": (Mapping[str, int], "Mapping[str, int]"),
        "abc.Iterable": (collections_abc.Iterable[int], "Iterable[int]"),
        "heterogeneous tuple": (tuple[int, str], "tuple[int, str]"),
        "typing.Tuple": (Tuple[int, str], "tuple[int, str]"),
        "homogeneous tuple": (tuple[int, ...], "tuple[int, ...]"),
        "nested": (dict[str, list[int | None]], "dict[str, list[int | None]]"),
        "type": (type[int], "type[int]"),
        "typing.Type": (Type[int], "type[int]"),
        "type[Any]": (type[Any], "type[Any]"),
    }

    for label, (annotation, text) in cases.items():
        with subtests.test(label):
            assert format_annotation(annotation) == text


def test_format_annotation_bare_generics(subtests) -> None:
    """Verify unsubscripted generics read as their plain name."""

    with subtests.test("bare list"):
        assert format_annotation(list) == "list"

    with subtests.test("bare typing.Callable"):
        assert format_annotation(typing.Callable) == "Callable"


def test_format_annotation_unions(subtests) -> None:
    """Verify Union, Optional and the | spelling all read as 'A | B'."""
    cases = {
        "Union": (Union[int, str], "int | str"),
        "Optional": (Optional[int], "int | None"),
        "pipe": (int | str | None, "int | str | None"),
        "union of generics": (list[int] | set[int], "list[int] | set[int]"),
    }

    for label, (annotation, text) in cases.items():
        with subtests.test(label):
            assert format_annotation(annotation) == text


def test_format_annotation_literal(subtests) -> None:
    """Verify Literal shows its values, not nested annotations."""

    with subtests.test("strings"):
        assert format_annotation(Literal["a", "b"]) == "Literal['a', 'b']"

    with subtests.test("mixed values"):
        assert format_annotation(Literal["a", 1, True, None]) == "Literal['a', 1, True, None]"


def test_format_annotation_callable(subtests) -> None:
    """Verify Callable shows its argument list."""

    with subtests.test("with signature"):
        assert format_annotation(Callable[[int, str], bool]) == "Callable[[int, str], bool]"

    with subtests.test("ellipsis arguments"):
        assert format_annotation(Callable[..., int]) == "Callable[..., int]"

    with subtests.test("no arguments"):
        assert format_annotation(Callable[[], int]) == "Callable[[], int]"


def test_format_annotation_annotated(subtests) -> None:
    """Verify Annotated shows only the metadata that takes part in validation."""

    with subtests.test("Rule metadata"):
        assert format_annotation(Annotated[int, DummyRule()]) == "Annotated[int, > 0]"

    with subtests.test("callable metadata"):
        assert format_annotation(Annotated[int, is_even]) == "Annotated[int, is_even]"

    with subtests.test("several validating items"):
        assert format_annotation(Annotated[int, DummyRule(), is_even]) == "Annotated[int, > 0, is_even]"

    with subtests.test("ignored metadata is invisible"):
        assert format_annotation(Annotated[int, "docs"]) == "int"

    with subtests.test("ignored metadata next to a rule"):
        assert format_annotation(Annotated[int, "docs", DummyRule()]) == "Annotated[int, > 0]"


def test_format_annotation_rule_instance_describes_itself() -> None:
    """Verify a Rule used directly as an annotation is described through its own describe()."""
    assert format_annotation(DummyRule()) == "> 0"
    assert format_annotation(list[DummyRule()]) == "list[> 0]"


def test_format_annotation_unknown_objects_fall_back_to_repr() -> None:
    """Verify an unrecognized object never raises and is shown via repr()."""
    assert format_annotation("UnparsedForwardRef") == "'UnparsedForwardRef'"
    assert format_annotation(42) == "42"
