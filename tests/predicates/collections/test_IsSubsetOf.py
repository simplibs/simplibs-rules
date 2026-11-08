"""Tests for the IsSubsetOf collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections import IsSubsetOf


def _generator(*items):
    yield from items


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_is_subset_of_contract(subtests):
    """Verify the complete contract of IsSubsetOf rule using master orchestrator."""
    rule = IsSubsetOf({"admin", "editor", "viewer"})

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            ["admin"],
            ["admin", "editor"],
            ("viewer",),
            set(),
            [],
        ],
        invalid_values=[
            ["admin", "superuser"],
            ["guest"],
            123,
            None,
            _generator("admin"),   # one-shot iterator — rejected even though its items fit the reference
            iter(["admin", "editor"]),
        ],
        expected_description="subset of {'admin', 'editor', 'viewer'}",
        rule_factory=IsSubsetOf,
        invalid_init_params=[
            ((123,), {}),       # Non-container reference parameter raises ParamError
            (("string",), {}),   # String reference raises ParamError
        ],
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DETAILED DIAGNOSTIC CARD TEST
# ==============================================================================

def test_is_subset_of_extra_elements_exception(subtests):
    """Verify diagnosis (ValueError) when the collection contains elements outside reference."""
    rule = IsSubsetOf([1, 2, 3, 4, 5])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([1, 2, 99], Kwargs(value_name="selected_ids")),
        exception_type=ValidationError,
        label="selected_ids",
        value=[1, 2, 99],
        error_name="IS_SUBSET_OF_ERROR",
        expected="subset of {1, 2, 3, 4, 5}",
        problem="Value contains element(s) not in reference: {99}.",
        how_to_fix="Remove element(s) not in {1, 2, 3, 4, 5}: {99}.",
        exception=ValueError,
        verbose=False,
    )


def test_is_subset_of_non_iterable_exception(subtests):
    """Verify diagnosis (TypeError) when the object is not iterable."""
    rule = IsSubsetOf(["a", "b", "c"])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(50, Kwargs(value_name="input_val")),
        exception_type=ValidationError,
        label="input_val",
        value=50,
        error_name="IS_SUBSET_OF_ERROR",
        expected="subset of {'a', 'b', 'c'}",
        problem="Value 50 of type 'int' is not iterable.",
        how_to_fix="Provide an iterable container (e.g., list, tuple, set).",
        exception=TypeError,
        verbose=False,
    )


def test_is_subset_of_unhashable_elements_exception(subtests):
    """Verify diagnosis (ValueError) when the value contains unhashable elements."""
    rule = IsSubsetOf([1, 2, 3])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([[1, 2]], Kwargs(value_name="nested_lists")),
        exception_type=ValidationError,
        label="nested_lists",
        value=[[1, 2]],
        error_name="IS_SUBSET_OF_ERROR",
        expected="subset of {1, 2, 3}",
        problem="Value [[1, 2]] contains unhashable elements that cannot be compared as a set.",
        how_to_fix="Ensure all elements in the container are hashable (e.g., strings, numbers, tuples).",
        exception=ValueError,
        verbose=False,
    )


def test_is_subset_of_one_shot_iterator_exception(subtests):
    """Verify diagnosis (TypeError) when the value is a one-shot iterator."""
    rule = IsSubsetOf({1, 2, 3})
    generator = _generator(1, 9)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(generator, Kwargs(value_name="items")),
        exception_type=ValidationError,
        label="items",
        error_name="IS_SUBSET_OF_ERROR",
        expected="subset of {1, 2, 3}",
        problem=(
            "Value of type 'generator' is a one-shot iterator: "
            "checking its items would consume it."
        ),
        how_to_fix="Pass a list, tuple or set (e.g. list(value)) instead of the iterator.",
        exception=TypeError,
        verbose=False,
    )
    assert list(generator) == [1, 9]   # still untouched after the failed validation


def test_is_subset_of_describe():
    """Verify the description phrase."""
    assert IsSubsetOf({"a", "b"}).describe() == "subset of {'a', 'b'}"


# ==============================================================================
# 3. ONE-SHOT ITERATORS & NON-LIST CONTAINERS
# ==============================================================================

def test_is_subset_of_rejects_one_shot_iterator_untouched():
    """Verify an iterator is rejected before it is consumed (even when its items fit the reference)."""
    rule = IsSubsetOf({1, 2, 3})
    generator = _generator(1, 2)

    assert rule.is_valid(generator) is False
    assert list(generator) == [1, 2]


def test_is_subset_of_rejects_every_kind_of_one_shot_iterator(subtests):
    """Verify generators and the common iterator-returning builtins are all rejected."""
    rule = IsSubsetOf({1, 2, 3})
    factories = {
        "generator": lambda: _generator(1, 2),
        "iter(list)": lambda: iter([1, 2]),
        "map": lambda: map(int, "12"),
        "filter": lambda: filter(None, [1, 2]),
    }

    for name, factory in factories.items():
        with subtests.test(name):
            assert rule.is_valid(factory()) is False


def test_is_subset_of_accepts_non_list_reiterable_containers(subtests):
    """Verify re-iterable containers other than list/tuple/set are still validated by their items."""
    rule = IsSubsetOf({1, 2, 3, 4})

    with subtests.test("range"):
        assert rule.is_valid(range(1, 4)) is True

    with subtests.test("frozenset"):
        assert rule.is_valid(frozenset({1, 2})) is True

    with subtests.test("dict iterates its keys"):
        assert rule.is_valid({1: "a", 2: "b"}) is True

    with subtests.test("dict view with an element outside the reference"):
        assert rule.is_valid({"a": 99}.values()) is False


def test_is_subset_of_class_object_is_rejected():
    """Verify a class object is not treated as an iterable value."""
    assert IsSubsetOf({1}).is_valid(list) is False


def test_is_subset_of_describe_abbreviates_a_long_reference() -> None:
    """Verify a reference too long to read is described by its size, so composed descriptions stay readable."""
    assert IsSubsetOf(set(range(100))).describe() == "subset of set(size=100)"
