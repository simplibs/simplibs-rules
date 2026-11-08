"""Tests for the ForEachValue container rule."""

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
from simplibs.rules.containers import AllOf, AnyOf, Compose, ForEach, ForEachValue
from simplibs.rules.predicates.numeric import IsInteger
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


class _NoItemsMapping(_CustomMapping):
    """A mapping whose items() must never be called."""

    def items(self):
        raise AssertionError("items() must not be called while the mapping is valid")


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_for_each_value_contract(subtests):
    """Verify the complete contract of ForEachValue using the master orchestrator."""
    # All values of a mapping must be numbers > 0
    rule = ForEachValue(GreaterThan(0))

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[
            {"a": 1, "b": 2},
            {1: 5},
            MappingProxyType({"x": 3}),
            {},  # Empty mapping is trivially valid (all() returns True)
        ],
        invalid_values=[
            {"a": 1, "b": -2},   # Second value violates rule (<= 0)
            {"a": "text"},       # Value violates comparison
            [1, 2],              # Not a mapping
            123,                 # Not a mapping
            None,                # Not a mapping
        ],
        expected_description="each value: > 0",
        rule_factory=ForEachValue,
        invalid_init_params=[
            (("not_callable",), {}),  # Non-callable rule raises ParamError
            ((None,), {}),            # None instead of rule raises ParamError
        ],
        deep_check=True,
        check_value=False,  # ForEachValue delegates to the values -> exc.value is the failed value, not the whole mapping
        verbose=False,
    )


# ==============================================================================
# 2. DIAGNOSTIC CARD TEST & LABELS
# ==============================================================================

def test_for_each_value_names_the_failing_value_by_its_key(subtests):
    """Verify the label carries the key of the failing value, not its position."""
    rule = ForEachValue(IsInteger())

    # The value stored under "b" (second one) fails on IsInteger
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=({"a": 1, "b": "x", "c": 3}, Kwargs(value_name="opts")),
        exception_type=ValidationError,
        label="opts['b']",
        value="x",
        expected="integer",
        verbose=False,
    )


def test_for_each_value_label_does_not_depend_on_the_order(subtests) -> None:
    """Verify the same failing entry gets the same label wherever it stands (the original defect)."""
    rule = ForEachValue(IsInteger())

    with subtests.test("failing entry second"):
        assert rule.build_exception({"a": 1, "zz": "x"}, value_name="opts").label == "opts['zz']"

    with subtests.test("failing entry first"):
        assert rule.build_exception({"zz": "x", "a": 1}, value_name="opts").label == "opts['zz']"

    with subtests.test("failing entry alone"):
        assert rule.build_exception({"zz": "x"}, value_name="opts").label == "opts['zz']"


@pytest.mark.parametrize(
    "key, expected_label",
    [
        (2, "opts[2]"),
        (None, "opts[None]"),
        (("x", 1), "opts[('x', 1)]"),
        (2.5, "opts[2.5]"),
        (True, "opts[True]"),
    ],
    ids=["int", "None", "tuple", "float", "bool"],
)
def test_for_each_value_label_spells_the_key_by_its_repr(key, expected_label) -> None:
    """Verify keys of any hashable type appear in the label as their repr."""
    rule = ForEachValue(IsInteger())

    exc = rule.build_exception({"ok": 1, key: "x"}, value_name="opts")

    assert exc.label == expected_label
    assert exc.value == "x"


def test_for_each_value_label_without_a_name() -> None:
    """Verify the label is only the bracket part when no value_name is given."""
    rule = ForEachValue(IsInteger())

    assert rule.build_exception({"b": "x"}).label == "['b']"
    assert rule.build_exception({"b": "x"}, value_name=None).label == "['b']"
    assert rule.build_exception({"b": "x"}, value_name="").label == "['b']"


def test_for_each_value_reports_the_first_failing_value() -> None:
    """Verify only the first failing value (in iteration order) is reported."""
    rule = ForEachValue(IsInteger())

    exc = rule.build_exception({"a": 1, "b": "x", "c": "y"}, value_name="opts")

    assert exc.label == "opts['b']"
    assert exc.value == "x"


def test_for_each_value_passes_the_context_through() -> None:
    """Verify the context text reaches the child exception."""
    rule = ForEachValue(IsInteger())

    exc = rule.build_exception({"a": "x"}, value_name="opts", context="loading options")

    assert exc.context == "loading options"


def test_for_each_value_rule_inside_a_value_extends_the_label() -> None:
    """Verify a nested rule builds on the key label, e.g. the second item of a list stored under 'a'."""
    rule = ForEachValue(ForEach(IsInteger()))

    exc = rule.build_exception({"a": [1, "q"]}, value_name="opts")

    assert exc.label == "opts['a'][1]"
    assert exc.value == "q"


def test_for_each_value_nested_in_a_value_extends_the_label() -> None:
    """Verify a mapping inside a mapping is named all the way down."""
    rule = ForEachValue(ForEachValue(IsInteger()))

    exc = rule.build_exception({"db": {"port": "x"}}, value_name="config")

    assert exc.label == "config['db']['port']"
    assert exc.value == "x"


def test_for_each_value_shortens_a_long_key_in_the_label() -> None:
    """Verify a very long key does not swamp the label."""
    rule = ForEachValue(IsInteger())
    key = "k" * 100

    exc = rule.build_exception({key: "x"}, value_name="opts")

    assert exc.label == f"opts[{repr(key)[:37]}...]"
    assert exc.value == "x"


def test_for_each_value_non_mapping_delegates_to_is_instance(subtests) -> None:
    """Verify a value that is not a mapping fails on the mapping check, not on an invented entry."""
    rule = ForEachValue(IsInteger())

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
def test_for_each_value_accepts_any_mapping(value) -> None:
    """Verify every collections.abc.Mapping is walked, not only dict."""
    assert ForEachValue(IsInteger()).is_valid(value) is True


@pytest.mark.parametrize(
    "value",
    [[1], (1,), {1}, frozenset({1}), "abc", 123, None, iter([1])],
    ids=["list", "tuple", "set", "frozenset", "str", "int", "None", "iterator"],
)
def test_for_each_value_rejects_what_is_not_a_mapping(value) -> None:
    """Verify an iterable of would-be values is not enough: the value has to be a mapping."""
    assert ForEachValue(IsInteger()).is_valid(value) is False


def test_for_each_value_does_not_look_at_the_keys() -> None:
    """Verify only values are checked; keys may be anything."""
    rule = ForEachValue(IsInteger())

    assert rule.is_valid({"a": 1, 2: 3, None: 4, (1, 2): 5}) is True


def test_for_each_value_is_valid_does_not_touch_items() -> None:
    """Verify the happy path walks the values only; keys are looked up just when an error is built."""
    rule = ForEachValue(IsInteger())

    assert rule.is_valid(_NoItemsMapping({"a": 1, "b": 2})) is True


def test_for_each_value_with_plain_callable_predicate() -> None:
    """Verify functionality with a plain function / lambda expression instead of a Rule instance."""
    rule = ForEachValue(lambda item: isinstance(item, str) and item.startswith("a"))

    assert rule.is_valid({1: "apple", 2: "avocado"}) is True
    assert rule.is_valid({1: "apple", 2: "banana"}) is False

    exc = rule.build_exception({1: "apple", 2: "banana"}, value_name="opts")

    assert isinstance(exc, ValidationError)
    assert exc.label == "opts[2]"
    assert exc.value == "banana"


def test_for_each_value_does_not_change_the_mapping() -> None:
    """Verify validation leaves the mapping as it was."""
    data = {"a": 1, "b": 2}
    rule = ForEachValue(IsInteger())

    rule.is_valid(data)
    rule.build_exception({**data, "c": "x"})

    assert data == {"a": 1, "b": 2}


def test_for_each_value_unreachable_fallback() -> None:
    """Verify fallback exception (FOR_EACH_VALUE_UNREACHABLE_ERROR) when no value fails during error construction."""
    rule = ForEachValue(IsInteger())

    # Manually calling build_exception with a mapping where no value fails:
    exc = rule.build_exception({"a": 1}, value_name="valid_mapping")

    assert isinstance(exc, ValidationError)
    assert exc.error_name == "FOR_EACH_VALUE_UNREACHABLE_ERROR"
    assert exc.label == "valid_mapping"
    assert exc.exception is RuntimeError


def test_for_each_value_constructor_names_the_rule_in_the_param_error() -> None:
    """Verify a non-callable argument raises a ParamError that names ForEachValue and suggests a fitting example."""
    with pytest.raises(ParamError) as info:
        ForEachValue("not_callable")

    assert info.value.label == "ForEachValue.rule"
    assert "ForEachValue(IsInteger())" in str(info.value.how_to_fix)


# ==============================================================================
# 4. DESCRIPTION TEST
# ==============================================================================

def is_a(value: Any) -> bool:
    return True


def is_b(value: Any) -> bool:
    return True


def test_for_each_value_describe(subtests):
    """Verify that ForEachValue describes itself as 'each value: <rule>', parenthesizing compound operands."""

    with subtests.test("simple operand"):
        assert ForEachValue(is_a).describe() == "each value: is_a"

    with subtests.test("Rule operand"):
        assert ForEachValue(IsInteger()).describe() == "each value: int"

    with subtests.test("AnyOf operand is parenthesized"):
        assert ForEachValue(AnyOf(is_a, is_b)).describe() == "each value: (is_a | is_b)"

    with subtests.test("AllOf operand is parenthesized"):
        assert ForEachValue(AllOf(is_a, is_b)).describe() == "each value: (is_a & is_b)"

    with subtests.test("Compose operand is parenthesized"):
        assert ForEachValue(Compose(str.strip, is_a)).describe() == "each value: (after strip: is_a)"
