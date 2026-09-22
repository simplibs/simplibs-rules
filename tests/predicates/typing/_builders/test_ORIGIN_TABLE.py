from collections import abc as collections_abc
import types
import typing

from simplibs.rules.predicates.typing._builders.build_annotated_rule import (
    build_annotated_rule,
)
from simplibs.rules.predicates.typing._builders.build_any_of_rule import (
    build_any_of_rule,
)
from simplibs.rules.predicates.typing._builders.build_callable_rule import (
    build_callable_rule,
)
from simplibs.rules.predicates.typing._builders.build_elements_rule import (
    build_elements_rule,
)
from simplibs.rules.predicates.typing._builders.build_key_value_rule import (
    build_key_value_rule,
)
from simplibs.rules.predicates.typing._builders.build_literal_rule import (
    build_literal_rule,
)
from simplibs.rules.predicates.typing._builders.build_tuple_rule import (
    build_tuple_rule,
)
from simplibs.rules.predicates.typing._builders.build_type_rule import (
    build_type_rule,
)
from simplibs.rules.predicates.typing._builders.ORIGIN_TABLE import ORIGIN_TABLE


def test_origin_table_elements_mapping() -> None:
    """Verify sequence and set collection origins map correctly to build_elements_rule."""
    elements_origins = [
        list,
        set,
        frozenset,
        collections_abc.Iterable,
        collections_abc.Sequence,
        collections_abc.Collection,
        typing.Iterable,
        typing.Sequence,
        typing.Collection,
        typing.List,
        typing.Set,
        typing.FrozenSet,
    ]
    for origin in elements_origins:
        assert ORIGIN_TABLE[origin] is build_elements_rule


def test_origin_table_key_value_mapping() -> None:
    """Verify mapping origins map correctly to build_key_value_rule."""
    mapping_origins = [
        dict,
        collections_abc.Mapping,
        collections_abc.MutableMapping,
        typing.Mapping,
        typing.MutableMapping,
        typing.Dict,
    ]
    for origin in mapping_origins:
        assert ORIGIN_TABLE[origin] is build_key_value_rule


def test_origin_table_special_constructs_mapping() -> None:
    """Verify special origins (Union, Literal, Type, Callable, Annotated, tuple) map to respective builders."""
    assert ORIGIN_TABLE[tuple] is build_tuple_rule
    assert ORIGIN_TABLE[typing.Tuple] is build_tuple_rule

    assert ORIGIN_TABLE[typing.Union] is build_any_of_rule
    assert ORIGIN_TABLE[types.UnionType] is build_any_of_rule

    assert ORIGIN_TABLE[typing.Literal] is build_literal_rule

    assert ORIGIN_TABLE[type] is build_type_rule
    assert ORIGIN_TABLE[typing.Type] is build_type_rule

    assert ORIGIN_TABLE[collections_abc.Callable] is build_callable_rule
    assert ORIGIN_TABLE[typing.Callable] is build_callable_rule

    assert ORIGIN_TABLE[typing.Annotated] is build_annotated_rule