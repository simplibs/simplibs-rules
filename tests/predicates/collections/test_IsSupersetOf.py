"""Tests for the IsSupersetOf collection rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.collections import IsSupersetOf


def _generator(*items):
    yield from items


# ==============================================================================
# 1. CONTRACT TEST (Master Contract)
# ==============================================================================

def test_is_superset_of_contract(subtests):
    """Verify the complete contract of IsSupersetOf rule using master orchestrator."""
    rule = IsSupersetOf({"read", "write"})

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            ["read", "write"],
            ["read", "write", "execute"],
            {"read", "write", "admin"},
        ],
        invalid_values=[
            ["read"],
            ["write"],
            ["execute"],
            [],
            123,
            None,
            _generator("read", "write"),   # one-shot iterator — rejected even though it holds every required item
            iter(["read", "write", "admin"]),
        ],
        expected_description="superset of {'read', 'write'}",
        rule_factory=IsSupersetOf,
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

def test_is_superset_of_missing_elements_exception(subtests):
    """Verify diagnosis (ValueError) when required elements are missing from the collection."""
    rule = IsSupersetOf(["read", "write", "execute"])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(["read"], Kwargs(value_name="permissions")),
        exception_type=ValidationError,
        label="permissions",
        value=["read"],
        error_name="IS_SUPERSET_OF_ERROR",
        expected="superset of {'execute', 'read', 'write'}",
        problem="Value is missing required element(s): {'execute', 'write'}.",
        how_to_fix="Include element(s): {'execute', 'write'}.",
        exception=ValueError,
        verbose=False,
    )


def test_is_superset_of_non_iterable_exception(subtests):
    """Verify diagnosis (TypeError) when the object is not iterable."""
    rule = IsSupersetOf(["a", "b"])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(100, Kwargs(value_name="raw_val")),
        exception_type=ValidationError,
        label="raw_val",
        value=100,
        error_name="IS_SUPERSET_OF_ERROR",
        expected="superset of {'a', 'b'}",
        problem="Value 100 of type 'int' is not iterable.",
        how_to_fix="Provide an iterable container (e.g., list, tuple, set).",
        exception=TypeError,
        verbose=False,
    )


def test_is_superset_of_unhashable_elements_exception(subtests):
    """Verify diagnosis (ValueError) when the value contains unhashable elements."""
    rule = IsSupersetOf([1, 2])

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([[1, 2]], Kwargs(value_name="nested")),
        exception_type=ValidationError,
        label="nested",
        value=[[1, 2]],
        error_name="IS_SUPERSET_OF_ERROR",
        expected="superset of {1, 2}",
        problem="Value [[1, 2]] contains unhashable elements that cannot be compared as a set.",
        how_to_fix="Ensure all elements in the container are hashable (e.g., strings, numbers, tuples).",
        exception=ValueError,
        verbose=False,
    )


def test_is_superset_of_one_shot_iterator_exception(subtests):
    """Verify diagnosis (TypeError) when the value is a one-shot iterator."""
    rule = IsSupersetOf({1, 2})
    generator = _generator(1)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(generator, Kwargs(value_name="items")),
        exception_type=ValidationError,
        label="items",
        error_name="IS_SUPERSET_OF_ERROR",
        expected="superset of {1, 2}",
        problem=(
            "Value of type 'generator' is a one-shot iterator: "
            "checking its items would consume it."
        ),
        how_to_fix="Pass a list, tuple or set (e.g. list(value)) instead of the iterator.",
        exception=TypeError,
        verbose=False,
    )
    assert list(generator) == [1]   # still untouched after the failed validation


def test_is_superset_of_describe():
    """Verify the description phrase."""
    assert IsSupersetOf({"a", "b"}).describe() == "superset of {'a', 'b'}"


# ==============================================================================
# 3. ONE-SHOT ITERATORS & NON-LIST CONTAINERS
# ==============================================================================

def test_is_superset_of_rejects_one_shot_iterator_untouched():
    """Verify an iterator is rejected before it is consumed (even when it contains the reference)."""
    rule = IsSupersetOf({1})
    generator = _generator(1, 2)

    assert rule.is_valid(generator) is False
    assert list(generator) == [1, 2]


def test_is_superset_of_rejects_every_kind_of_one_shot_iterator(subtests):
    """Verify generators and the common iterator-returning builtins are all rejected."""
    rule = IsSupersetOf({1})
    factories = {
        "generator": lambda: _generator(1, 2),
        "iter(list)": lambda: iter([1, 2]),
        "map": lambda: map(int, "12"),
        "filter": lambda: filter(None, [1, 2]),
    }

    for name, factory in factories.items():
        with subtests.test(name):
            assert rule.is_valid(factory()) is False


def test_is_superset_of_accepts_non_list_reiterable_containers(subtests):
    """Verify re-iterable containers other than list/tuple/set are still validated by their items."""
    rule = IsSupersetOf({1, 2})

    with subtests.test("range"):
        assert rule.is_valid(range(5)) is True

    with subtests.test("frozenset"):
        assert rule.is_valid(frozenset({1, 2, 3})) is True

    with subtests.test("dict iterates its keys"):
        assert rule.is_valid({1: "a", 2: "b", 3: "c"}) is True

    with subtests.test("dict view missing a required element"):
        assert rule.is_valid({"a": 1}.values()) is False


def test_is_superset_of_class_object_is_rejected():
    """Verify a class object is not treated as an iterable value."""
    assert IsSupersetOf({1}).is_valid(list) is False
