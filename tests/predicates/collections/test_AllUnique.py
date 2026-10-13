"""Tests for the AllUnique collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections import AllUnique


def _generator(*items):
    yield from items


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_all_unique_contract(subtests):
    """Verify the complete contract of AllUnique rule using master orchestrator."""
    rule = AllUnique()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            [1, 2, 3],
            ("a", "b", "c"),
            {10, 20, 30},
            [],
            "abc",
            range(3),
        ],
        invalid_values=[
            [1, 2, 2, 3],
            ("a", "a", "b"),
            "aba",
            123,
            None,
            _generator(1, 2, 3),   # one-shot iterator — rejected even though its items are unique
            iter([1, 2, 3]),
        ],
        expected_description="all unique",
        rule_factory=AllUnique,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_all_unique_duplicates_exception(subtests):
    """Verify diagnosis (ValueError) when the collection contains duplicate items."""
    rule = AllUnique()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([1, 2, 2, 3, 1], Kwargs(value_name="numbers")),
        exception_type=ValidationError,
        label="numbers",
        value=[1, 2, 2, 3, 1],
        error_name="ALL_UNIQUE_ERROR",
        expected="all-unique items",
        problem="Value contains duplicate item(s): [2, 1].",
        how_to_fix="Remove duplicate item(s): [2, 1].",
        exception=ValueError,
        verbose=False,
    )


def test_all_unique_non_iterable_exception(subtests):
    """Verify diagnosis (TypeError) when the object is not iterable."""
    rule = AllUnique()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(42, Kwargs(value_name="payload")),
        exception_type=ValidationError,
        label="payload",
        value=42,
        error_name="ALL_UNIQUE_ERROR",
        expected="all-unique items",
        problem="Value 42 of type 'int' is not iterable.",
        how_to_fix="Provide an iterable container (e.g., list, tuple, set).",
        exception=TypeError,
        verbose=False,
    )


def test_all_unique_one_shot_iterator_exception(subtests):
    """Verify diagnosis (TypeError) when the value is a one-shot iterator."""
    rule = AllUnique()
    generator = _generator(1, 1)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(generator, Kwargs(value_name="items")),
        exception_type=ValidationError,
        label="items",
        error_name="ALL_UNIQUE_ERROR",
        expected="all-unique items",
        problem=(
            "Value of type 'generator' is a one-shot iterator: "
            "checking its items would consume it."
        ),
        how_to_fix="Pass a list, tuple or set (e.g. list(value)) instead of the iterator.",
        exception=TypeError,
        verbose=False,
    )
    assert list(generator) == [1, 1]   # still untouched after the failed validation


# ==============================================================================
# 3. SPECIFIC EDGE CASES & UNHASHABLE TYPES
# ==============================================================================

def test_all_unique_unhashable_items():
    """Verify fallback behavior for unhashable objects (e.g., lists within a list)."""
    rule = AllUnique()

    # Unique lists
    assert rule.is_valid([[1, 2], [3, 4]]) is True

    # Duplicate unhashable lists
    assert rule.is_valid([[1, 2], [1, 2]]) is False


def test_all_unique_describe():
    """Verify the description phrase."""
    assert AllUnique().describe() == "all unique"


# ==============================================================================
# 4. ONE-SHOT ITERATORS & NON-LIST CONTAINERS
# ==============================================================================

def test_all_unique_rejects_one_shot_iterator_untouched():
    """Verify an iterator is rejected before it is consumed (even when its items are unique)."""
    rule = AllUnique()
    generator = _generator(1, 2, 3)

    assert rule.is_valid(generator) is False
    assert list(generator) == [1, 2, 3]


def test_all_unique_rejects_every_kind_of_one_shot_iterator(subtests):
    """Verify generators and the common iterator-returning builtins are all rejected."""
    rule = AllUnique()
    factories = {
        "generator": lambda: _generator(1, 2, 3),
        "iter(list)": lambda: iter([1, 2, 3]),
        "map": lambda: map(int, "123"),
        "filter": lambda: filter(None, [1, 2, 3]),
        "zip": lambda: zip("abc", "xyz"),
    }

    for name, factory in factories.items():
        with subtests.test(name):
            assert rule.is_valid(factory()) is False


def test_all_unique_accepts_non_list_reiterable_containers(subtests):
    """Verify re-iterable containers other than list/tuple/set are still validated by their items."""
    rule = AllUnique()

    with subtests.test("range"):
        assert rule.is_valid(range(5)) is True

    with subtests.test("dict iterates its (unique) keys"):
        assert rule.is_valid({"a": 1, "b": 1}) is True

    with subtests.test("dict view with unique items"):
        assert rule.is_valid({"a": 1, "b": 2}.values()) is True

    with subtests.test("dict view with duplicate items"):
        assert rule.is_valid({"a": 1, "b": 1}.values()) is False


def test_all_unique_class_object_is_not_iterable_and_does_not_raise():
    """Verify a class object (hasattr(list, '__iter__') is True) is rejected instead of raising."""
    assert AllUnique().is_valid(list) is False
