"""Tests for the ForEachKey container rule."""

from collections import OrderedDict
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any
import pytest

# Testing tools
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ParamError, ValidationError

# Rules
from simplibs.rules.containers import AllOf, AnyOf, Compose, ForEach, ForEachKey
from simplibs.rules.predicates.numeric import IsInteger
from simplibs.rules.predicates.strings import IsString
from simplibs.rules.predicates.comparisons import GreaterThan


class _CustomMapping(Mapping):
    """A mapping that is not a dict, to show the rule works on the Mapping contract."""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __getitem__(self, key: Any) -> Any:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_for_each_key_contract(subtests):
    """Verify the complete contract of ForEachKey using the master orchestrator."""
    # All keys of a mapping must be integers > 0
    rule = ForEachKey(GreaterThan(0))

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            {1: "a", 2: "b"},
            {5: None},
            MappingProxyType({3: 1}),
            {},  # Empty mapping is trivially valid (all() returns True)
        ],
        invalid_values=[
            {1: "a", -2: "b"},   # Second key violates rule (<= 0)
            {"text": 1},         # Key violates comparison
            [1, 2],              # Not a mapping
            123,                 # Not a mapping
            None,                # Not a mapping
        ],
        expected_description="each key: > 0",
        rule_factory=ForEachKey,
        invalid_init_params=[
            (("not_callable",), {}),  # Non-callable rule raises ParamError
            ((None,), {}),            # None instead of rule raises ParamError
        ],
        deep_check=True,
        check_value=False,  # ForEachKey delegates to the keys -> exc.value is the failed key, not the whole mapping
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST & LABELS
# ==============================================================================

def test_for_each_key_names_the_failing_key_in_the_label(subtests):
    """Verify the label carries the key itself, marked as a key, not a position."""
    rule = ForEachKey(IsInteger())

    # Key "b" (second one) fails on IsInteger
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=({1: "a", "b": "x", 3: "c"}, Kwargs(value_name="opts")),
        exception_type=ValidationError,
        label="opts[key 'b']",
        value="b",
        expected="integer",
        verbose=False,
    )


@pytest.mark.parametrize(
    "key, expected_label",
    [
        (1, "opts[key 1]"),
        (None, "opts[key None]"),
        ((1, 2), "opts[key (1, 2)]"),
        (2.5, "opts[key 2.5]"),
        (True, "opts[key True]"),
    ],
    ids=["int", "None", "tuple", "float", "bool"],
)
def test_for_each_key_label_spells_the_key_by_its_repr(key, expected_label) -> None:
    """Verify keys of any hashable type appear in the label as their repr."""
    rule = ForEachKey(IsString())

    exc = rule.build_exception({"ok": 1, key: 2}, value_name="opts")

    assert exc.label == expected_label
    assert exc.value == key


def test_for_each_key_label_without_a_name() -> None:
    """Verify the label is only the bracket part when no value_name is given."""
    rule = ForEachKey(IsString())

    assert rule.build_exception({1: "a"}).label == "[key 1]"
    assert rule.build_exception({1: "a"}, value_name=None).label == "[key 1]"
    assert rule.build_exception({1: "a"}, value_name="").label == "[key 1]"


def test_for_each_key_reports_the_first_failing_key() -> None:
    """Verify only the first failing key (in iteration order) is reported."""
    rule = ForEachKey(IsString())

    exc = rule.build_exception({"a": 1, 2: "x", 3: "y"}, value_name="opts")

    assert exc.label == "opts[key 2]"
    assert exc.value == 2


def test_for_each_key_passes_the_context_through() -> None:
    """Verify the context text reaches the child exception."""
    rule = ForEachKey(IsString())

    exc = rule.build_exception({1: "a"}, value_name="opts", context="loading options")

    assert exc.context == "loading options"


def test_for_each_key_rule_inside_a_composite_key_extends_the_label() -> None:
    """Verify a nested rule builds on the key label, e.g. the second part of a tuple key."""
    rule = ForEachKey(ForEach(IsInteger()))

    exc = rule.build_exception({(1, "x"): 0}, value_name="opts")

    assert exc.label == "opts[key (1, 'x')][1]"
    assert exc.value == "x"


def test_for_each_key_shortens_a_long_key_in_the_label() -> None:
    """Verify a very long key does not swamp the label, while the card still carries the whole key."""
    rule = ForEachKey(IsInteger())
    key = "k" * 100

    exc = rule.build_exception({key: 1}, value_name="opts")

    assert exc.label == f"opts[key {repr(key)[:37]}...]"
    assert exc.value == key


def test_for_each_key_non_mapping_delegates_to_is_instance(subtests) -> None:
    """Verify a value that is not a mapping fails on the mapping check, not on an invented key."""
    rule = ForEachKey(IsInteger())

    for value in ([1], ("a",), {"a"}, "abc", 123, None):
        with subtests.test(repr(value)):
            exc = rule.build_exception(value, value_name="payload")

            assert isinstance(exc, ValidationError)
            assert exc.error_name == "IS_INSTANCE_ERROR"
            assert exc.label == "payload"
            assert exc.value == value
            assert exc.exception is TypeError


# ==============================================================================
# 3. EDGE CASES & BEHAVIOR
# ==============================================================================

@pytest.mark.parametrize(
    "value",
    [
        {"a": 1},
        OrderedDict(a=1),
        MappingProxyType({"a": 1}),
        _CustomMapping({"a": 1}),
        {},
    ],
    ids=["dict", "OrderedDict", "MappingProxyType", "custom Mapping", "empty"],
)
def test_for_each_key_accepts_any_mapping(value) -> None:
    """Verify every collections.abc.Mapping is walked, not only dict."""
    assert ForEachKey(IsString()).is_valid(value) is True


@pytest.mark.parametrize(
    "value",
    [["a"], ("a",), {"a"}, frozenset({"a"}), "abc", 123, None, iter(["a"])],
    ids=["list", "tuple", "set", "frozenset", "str", "int", "None", "iterator"],
)
def test_for_each_key_rejects_what_is_not_a_mapping(value) -> None:
    """Verify an iterable of would-be keys is not enough: the value has to be a mapping."""
    assert ForEachKey(IsString()).is_valid(value) is False


def test_for_each_key_does_not_look_at_the_values() -> None:
    """Verify only keys are checked; values may be anything."""
    rule = ForEachKey(IsString())

    assert rule.is_valid({"a": object(), "b": None, "c": [1, 2]}) is True


def test_for_each_key_with_plain_callable_predicate() -> None:
    """Verify functionality with a plain function / lambda expression instead of a Rule instance."""
    rule = ForEachKey(lambda key: isinstance(key, str) and key.startswith("a"))

    assert rule.is_valid({"apple": 1, "avocado": 2}) is True
    assert rule.is_valid({"apple": 1, "banana": 2}) is False

    exc = rule.build_exception({"apple": 1, "banana": 2}, value_name="opts")

    assert isinstance(exc, ValidationError)
    assert exc.label == "opts[key 'banana']"
    assert exc.value == "banana"


def test_for_each_key_does_not_change_the_mapping() -> None:
    """Verify validation leaves the mapping as it was."""
    data = {"a": 1, "b": 2}
    rule = ForEachKey(IsString())

    rule.is_valid(data)
    rule.build_exception({**data, 3: 4})

    assert data == {"a": 1, "b": 2}


def test_for_each_key_unreachable_fallback() -> None:
    """Verify fallback exception (FOR_EACH_KEY_UNREACHABLE_ERROR) when no key fails during error construction."""
    rule = ForEachKey(IsString())

    # Manually calling build_exception with a mapping where no key fails:
    exc = rule.build_exception({"a": 1}, value_name="valid_mapping")

    assert isinstance(exc, ValidationError)
    assert exc.error_name == "FOR_EACH_KEY_UNREACHABLE_ERROR"
    assert exc.label == "valid_mapping"
    assert exc.exception is RuntimeError


def test_for_each_key_constructor_names_the_rule_in_the_param_error() -> None:
    """Verify a non-callable argument raises a ParamError that names ForEachKey and suggests a fitting example."""
    with pytest.raises(ParamError) as info:
        ForEachKey("not_callable")

    assert info.value.label == "ForEachKey.rule"
    assert "ForEachKey(IsString())" in str(info.value.how_to_fix)


# ==============================================================================
# 4. DESCRIPTION TEST
# ==============================================================================

def is_a(value: Any) -> bool:
    return True


def is_b(value: Any) -> bool:
    return True


def test_for_each_key_describe(subtests):
    """Verify that ForEachKey describes itself as 'each key: <rule>', parenthesizing compound operands."""

    with subtests.test("simple operand"):
        assert ForEachKey(is_a).describe() == "each key: is_a"

    with subtests.test("Rule operand"):
        assert ForEachKey(IsString()).describe() == "each key: str"

    with subtests.test("AnyOf operand is parenthesized"):
        assert ForEachKey(AnyOf(is_a, is_b)).describe() == "each key: (is_a | is_b)"

    with subtests.test("AllOf operand is parenthesized"):
        assert ForEachKey(AllOf(is_a, is_b)).describe() == "each key: (is_a & is_b)"

    with subtests.test("Compose operand is parenthesized"):
        assert ForEachKey(Compose(str.strip, is_a)).describe() == "each key: (after strip: is_a)"
