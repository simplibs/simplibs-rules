"""Tests for the format_container helper function."""

from typing import Any
import pytest

from simplibs.rules.predicates._helpers.format_container import format_container


class UnsortableItem:
    """Helper class for testing unsortable elements in a set."""

    def __init__(self, val: int) -> None:
        self.val = val

    def __repr__(self) -> str:
        return f"Unsortable({self.val})"


# ==============================================================================
# 1. SET TESTS (Deterministic Sorting)
# ==============================================================================

def test_format_container_sorted_set(subtests):
    """Verify that a standard set of strings or numbers is sorted deterministically."""
    with subtests.test("strings"):
        # Output must be alphabetically sorted regardless of original element order
        s = {"c", "a", "b"}
        assert format_container(s) == "{'a', 'b', 'c'}"

    with subtests.test("integers"):
        s = {3, 1, 2}
        assert format_container(s) == "{1, 2, 3}"

    with subtests.test("empty_set"):
        # An empty set produces empty curly braces
        assert format_container(set()) == "{}"


def test_format_container_frozenset(subtests):
    """Verify that frozenset formats deterministically just like a set."""
    fs = frozenset(["write", "execute", "read"])
    assert format_container(fs) == "{'execute', 'read', 'write'}"


def test_format_container_unsortable_set(subtests):
    """Verify fallback to list conversion when a set element does not support sorting (TypeError)."""
    with subtests.test("mixed_types"):
        # In Python 3, int and str cannot be compared (sorted() raises TypeError)
        s = {1, "a"}
        result = format_container(s)
        # Output must start and end with curly braces and contain both elements
        assert result.startswith("{") and result.endswith("}")
        assert "'a'" in result
        assert "1" in result

    with subtests.test("custom_unsortable_objects"):
        obj1 = UnsortableItem(2)
        obj2 = UnsortableItem(1)
        s = {obj1, obj2}
        result = format_container(s)
        assert result.startswith("{") and result.endswith("}")
        assert "Unsortable(1)" in result
        assert "Unsortable(2)" in result


# ==============================================================================
# 2. OTHER CONTAINERS TESTS (Passthrough for repr)
# ==============================================================================

def test_format_container_passthrough_types(subtests):
    """Verify that sequence containers and dictionaries preserve their standard repr()."""
    with subtests.test("list"):
        lst = ["c", "a", "b"]
        assert format_container(lst) == "['c', 'a', 'b']"

    with subtests.test("tuple"):
        tup = (3, 1, 2)
        assert format_container(tup) == "(3, 1, 2)"

    with subtests.test("dict"):
        d = {"b": 2, "a": 1}
        assert format_container(d) == "{'b': 2, 'a': 1}"

    with subtests.test("string"):
        s = "hello"
        assert format_container(s) == "'hello'"