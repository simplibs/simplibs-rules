import collections.abc
from typing import Dict, Mapping, MutableMapping

import pytest

from simplibs.exception import ValidationError
from simplibs.rules.containers import AllOf, ForEachKey, ForEachValue
from simplibs.rules.predicates.introspection import IsInstance
from simplibs.rules.predicates.typing._builders.build_key_value_rule import (
    build_key_value_rule,
)


# ==============================================================================
# 1. STRUCTURE & VALIDITY
# ==============================================================================

def test_build_key_value_rule_subscripted() -> None:
    """Verify dict[str, int] constructs IsInstance, ForEachKey for keys, and ForEachValue for values."""
    rule = build_key_value_rule(dict[str, int])

    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 3
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], ForEachKey)
    assert isinstance(rule.rules[2], ForEachValue)

    assert rule.is_valid({"a": 1, "b": 2}) is True
    assert rule.is_valid({}) is True
    assert rule.is_valid({1: 1}) is False  # wrong key
    assert rule.is_valid({"a": "1"}) is False  # wrong value
    assert rule.is_valid([("a", 1)]) is False  # not a dict


def test_build_key_value_rule_unsubscripted() -> None:
    """Verify bare dict produces only an IsInstance(dict) rule."""
    rule = build_key_value_rule(Dict)

    assert isinstance(rule, IsInstance)
    assert rule.is_valid({"any": 123, 456: "thing"}) is True
    assert rule.is_valid("not_a_dict") is False


def test_build_key_value_rule_checks_the_mapping_type_first_then_keys_then_values() -> None:
    """Verify the order of the parts: type, keys, values (so a wrong key is reported before a wrong value)."""
    rule = build_key_value_rule(dict[str, int])

    assert [type(part) for part in rule.rules] == [IsInstance, ForEachKey, ForEachValue]


@pytest.mark.parametrize(
    "annotation, valid, invalid",
    [
        (dict[str, int], {"a": 1}, {"a": "x"}),
        (Dict[str, int], {"a": 1}, {"a": "x"}),
        (Mapping[str, int], {"a": 1}, {"a": "x"}),
        (MutableMapping[str, int], {"a": 1}, {"a": "x"}),
        (collections.abc.Mapping[str, int], {"a": 1}, {"a": "x"}),
        (collections.abc.MutableMapping[str, int], {"a": 1}, {"a": "x"}),
    ],
    ids=["dict", "typing.Dict", "typing.Mapping", "typing.MutableMapping", "abc.Mapping", "abc.MutableMapping"],
)
def test_build_key_value_rule_covers_every_mapping_spelling(annotation, valid, invalid) -> None:
    """Verify every mapping-shaped generic gets the same key and value rules."""
    rule = build_key_value_rule(annotation)

    assert rule.is_valid(valid) is True
    assert rule.is_valid(invalid) is False
    assert isinstance(rule.rules[1], ForEachKey)
    assert isinstance(rule.rules[2], ForEachValue)


def test_build_key_value_rule_describes_its_parts() -> None:
    """Verify the composed rule describes the type, the keys and the values separately."""
    rule = build_key_value_rule(dict[str, int])

    assert rule.rules[1].describe() == "each key: str"
    assert rule.rules[2].describe() == "each value: int"


# ==============================================================================
# 2. LABELS OF THE FAILING ENTRY (the defect this change fixes)
# ==============================================================================

@pytest.mark.parametrize(
    "value, expected_label, expected_value",
    [
        ({"a": 1, "b": "x"}, "opts['b']", "x"),     # was opts[1]
        ({"a": 1, "zz": "x"}, "opts['zz']", "x"),   # was opts[1]
        ({"b": "x", "a": 1}, "opts['b']", "x"),     # the order does not matter
        ({1: 1}, "opts[key 1]", 1),                 # was opts[0], indistinguishable from a value
    ],
    ids=["value b", "value zz", "value first", "key"],
)
def test_build_key_value_rule_names_the_failing_entry(value, expected_label, expected_value) -> None:
    """Verify a failing value is named by its key and a failing key is marked as a key."""
    rule = build_key_value_rule(dict[str, int])

    with pytest.raises(ValidationError) as info:
        rule.validate(value, value_name="opts")

    assert info.value.label == expected_label
    assert info.value.value == expected_value


@pytest.mark.parametrize(
    "value, expected_label",
    [
        ({"a": 1, "b": "x"}, "['b']"),
        ({1: 1}, "[key 1]"),
    ],
    ids=["value", "key"],
)
def test_build_key_value_rule_labels_without_a_name(value, expected_label) -> None:
    """Verify only the bracket part remains when the value has no name."""
    rule = build_key_value_rule(dict[str, int])

    with pytest.raises(ValidationError) as info:
        rule.validate(value)

    assert info.value.label == expected_label


def test_build_key_value_rule_reports_a_wrong_key_before_a_wrong_value() -> None:
    """Verify the keys are checked first, so an entry with both wrong is reported as a key."""
    rule = build_key_value_rule(dict[str, int])

    with pytest.raises(ValidationError) as info:
        rule.validate({1: "x"}, value_name="opts")

    assert info.value.label == "opts[key 1]"


def test_build_key_value_rule_reports_the_first_failing_value() -> None:
    """Verify only the first failing value (in iteration order) is reported."""
    rule = build_key_value_rule(dict[str, int])

    with pytest.raises(ValidationError) as info:
        rule.validate({"a": 1, "b": "x", "c": "y"}, value_name="opts")

    assert info.value.label == "opts['b']"


@pytest.mark.parametrize(
    "annotation",
    [
        dict[str, int],
        Dict[str, int],
        Mapping[str, int],
        MutableMapping[str, int],
        collections.abc.Mapping[str, int],
        collections.abc.MutableMapping[str, int],
    ],
    ids=["dict", "typing.Dict", "typing.Mapping", "typing.MutableMapping", "abc.Mapping", "abc.MutableMapping"],
)
def test_build_key_value_rule_labels_are_the_same_for_every_mapping_spelling(annotation) -> None:
    """Verify the label does not depend on how the mapping type is spelled."""
    rule = build_key_value_rule(annotation)

    with pytest.raises(ValidationError) as info:
        rule.validate({"a": 1, "b": "x"}, value_name="opts")

    assert info.value.label == "opts['b']"


def test_build_key_value_rule_not_a_mapping_fails_on_the_type_check() -> None:
    """Verify a value that is not a mapping is reported on the name itself, with no entry in the label."""
    rule = build_key_value_rule(dict[str, int])

    with pytest.raises(ValidationError) as info:
        rule.validate([("a", 1)], value_name="opts")

    assert info.value.label == "opts"
    assert info.value.error_name == "IS_INSTANCE_ERROR"


# ==============================================================================
# 3. NESTED ANNOTATIONS
# ==============================================================================

def test_build_key_value_rule_label_continues_into_a_list_value() -> None:
    """Verify a failing item of a list stored in a mapping is named all the way down."""
    rule = build_key_value_rule(dict[str, list[int]])

    with pytest.raises(ValidationError) as info:
        rule.validate({"a": [1, "q"]}, value_name="opts")

    assert info.value.label == "opts['a'][1]"
    assert info.value.value == "q"


def test_build_key_value_rule_label_continues_into_a_nested_mapping() -> None:
    """Verify a failing value of a mapping inside a mapping is named by both keys."""
    rule = build_key_value_rule(dict[str, dict[str, int]])

    with pytest.raises(ValidationError) as info:
        rule.validate({"db": {"port": "x"}}, value_name="config")

    assert info.value.label == "config['db']['port']"
    assert info.value.value == "x"


def test_build_key_value_rule_label_continues_into_a_composite_key() -> None:
    """Verify a failing part of a tuple key is named inside the key label."""
    rule = build_key_value_rule(dict[tuple[int, ...], int])

    with pytest.raises(ValidationError) as info:
        rule.validate({(1, "x"): 3}, value_name="opts")

    assert info.value.label == "opts[key (1, 'x')][1]"
    assert info.value.value == "x"


def test_build_key_value_rule_label_with_a_union_value() -> None:
    """Verify an optional value is named by its key like any other."""
    rule = build_key_value_rule(dict[str, int | None])

    assert rule.is_valid({"a": 1, "b": None}) is True

    with pytest.raises(ValidationError) as info:
        rule.validate({"a": 1, "b": "x"}, value_name="opts")

    assert info.value.label == "opts['b']"


def test_build_key_value_rule_long_key_is_shortened_in_the_label() -> None:
    """Verify a very long key does not swamp the label."""
    rule = build_key_value_rule(dict[str, int])
    key = "k" * 100

    with pytest.raises(ValidationError) as info:
        rule.validate({key: "x"}, value_name="opts")

    assert info.value.label == f"opts[{repr(key)[:37]}...]"
    assert info.value.value == "x"
