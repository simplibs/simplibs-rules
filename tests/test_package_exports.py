"""Tests for the public surface of simplibs.rules: __all__, the shortcuts and the two namespaces."""

import pytest

import simplibs.rules as package
from simplibs.exception import ValidationError
from simplibs.rules import (
    AllOf,
    AnyOf,
    Compose,
    Described,
    ForEach,
    ForEachKey,
    ForEachValue,
    NoneOf,
    Not,
)


def test_every_name_in_all_exists(subtests) -> None:
    """Verify nothing is promised in __all__ that the package does not provide."""
    for name in package.__all__:
        with subtests.test(name):
            assert hasattr(package, name)


def test_all_has_no_duplicates() -> None:
    """Verify every name is listed in __all__ exactly once."""
    names = package.__all__
    duplicates = sorted({name for name in names if names.count(name) > 1})

    assert duplicates == []


def test_rule_class_namespace_matches_the_package(subtests) -> None:
    """Verify every class in `rule_class` is the same object as the one exported by name."""
    for name, value in vars(package.rule_class).items():
        with subtests.test(name):
            assert name in package.__all__
            assert getattr(package, name) is value


def test_rules_namespace_matches_the_package(subtests) -> None:
    """Verify every shortcut in `rules` is the same object as the one exported by name."""
    for name, value in vars(package.rules).items():
        with subtests.test(name):
            assert name in package.__all__
            assert getattr(package, name) is value


@pytest.mark.parametrize(
    "shortcut, rule_class",
    [
        ("all_of", AllOf),
        ("any_of", AnyOf),
        ("compose", Compose),
        ("for_each", ForEach),
        ("for_each_key", ForEachKey),
        ("for_each_value", ForEachValue),
        ("none_of", NoneOf),
        ("negate", Not),
        ("described", Described),
    ],
)
def test_container_shortcuts_are_the_classes(shortcut, rule_class) -> None:
    """Verify each container shortcut is its class, from the package and from the `rules` namespace."""
    assert getattr(package, shortcut) is rule_class
    assert getattr(package.rules, shortcut) is rule_class


def test_container_classes_are_in_the_rule_class_namespace() -> None:
    """Verify the mapping rules are reachable through `rule_class`, next to the older containers."""
    assert package.rule_class.ForEachKey is ForEachKey
    assert package.rule_class.ForEachValue is ForEachValue


def test_for_each_value_shortcut_names_the_failing_key() -> None:
    """Verify the shortcuts work together: a failing value is named by its key."""
    rule = package.for_each_value(package.is_integer)

    with pytest.raises(ValidationError) as info:
        rule.validate({"a": 1, "b": "x"}, value_name="opts")

    assert info.value.label == "opts['b']"


def test_for_each_key_shortcut_marks_the_failing_key() -> None:
    """Verify the shortcuts work together: a failing key is marked as a key."""
    rule = package.rules.for_each_key(package.rules.is_string)

    with pytest.raises(ValidationError) as info:
        rule.validate({"a": 1, 2: 2}, value_name="opts")

    assert info.value.label == "opts[key 2]"
