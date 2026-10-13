"""Tests for the IsReiterable rule."""

import io
from collections import deque
from typing import Any

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.introspection import IsReiterable


def _generator():
    yield 1
    yield 2


class _FreshIterator:
    """Iterable whose __iter__ returns a NEW iterator every time -> re-iterable."""

    def __iter__(self):
        return iter([1, 2])


class _SelfIterator:
    """Iterator that returns itself from __iter__ -> one-shot."""

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration


class _LegacySequence:
    """Iterable only through the legacy __getitem__ protocol (no __iter__)."""

    def __getitem__(self, index: int) -> int:
        if index > 2:
            raise IndexError
        return index


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_is_reiterable_contract(subtests):
    """Verify the complete contract of the IsReiterable rule."""
    rule = IsReiterable()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            "text", b"bytes", [1, 2], (1, 2), {"a": 1}, {1, 2}, frozenset({1}),
            range(3), {"a": 1}.keys(), {"a": 1}.values(), deque([1]), _FreshIterator(),
        ],
        invalid_values=[
            _generator(), iter([1, 2]), map(str, [1]), zip([1], [2]), filter(None, [1]),
            enumerate([1]), reversed([1]), _SelfIterator(),
            123, 3.14, True, None,
        ],
        expected_description="re-iterable",
        rule_factory=IsReiterable,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARDS
# ==============================================================================

def test_is_reiterable_exception_not_iterable(subtests):
    """Verify diagnosis (TypeError) when value is not iterable at all."""
    rule = IsReiterable()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(123, Kwargs(value_name="items")),
        exception_type=ValidationError,
        label="items",
        value=123,
        error_name="IS_REITERABLE_ERROR",
        expected="re-iterable value (e.g. list, tuple, set), not a one-shot iterator",
        problem="Value 123 of type 'int' is not iterable.",
        how_to_fix="Provide a re-iterable container (e.g., list, tuple, set).",
        exception=TypeError,
        verbose=False,
    )


def test_is_reiterable_exception_one_shot_iterator(subtests):
    """Verify diagnosis (TypeError) when value is a one-shot iterator."""
    rule = IsReiterable()
    generator = _generator()

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(generator, Kwargs(value_name="items")),
        exception_type=ValidationError,
        label="items",
        value=generator,
        error_name="IS_REITERABLE_ERROR",
        expected="re-iterable value (e.g. list, tuple, set), not a one-shot iterator",
        problem=(
            "Value of type 'generator' is a one-shot iterator: checking its items "
            "would consume it, so the receiving code would get it exhausted."
        ),
        how_to_fix=(
            "Pass a list, tuple or set (e.g. list(value)) instead of the iterator, "
            "or annotate the parameter as plain Iterable (without an item type)."
        ),
        exception=TypeError,
        verbose=False,
    )


# ==============================================================================
# 3. BEHAVIOR
# ==============================================================================

def test_is_reiterable_never_touches_the_value():
    """Verify validating (or failing) never advances an iterator."""
    rule = IsReiterable()
    generator = _generator()

    assert rule.is_valid(generator) is False
    assert rule.build_exception(generator, "items") is not None
    assert list(generator) == [1, 2]


def test_is_reiterable_file_objects_are_one_shot():
    """Verify file-like objects (iterators over lines) are rejected."""
    assert IsReiterable().is_valid(io.StringIO("a\nb")) is False


def test_is_reiterable_class_object_is_not_a_value():
    """Verify a class object is not treated as an iterable value."""
    assert IsReiterable().is_valid(list) is False


def test_is_reiterable_legacy_getitem_protocol_is_not_recognized():
    """Verify objects iterable only via __getitem__ are not accepted (ABC check, same as IsInstance(Iterable))."""
    assert IsReiterable().is_valid(_LegacySequence()) is False


def test_is_reiterable_describe():
    """Verify the description phrase."""
    assert IsReiterable().describe() == "re-iterable"
