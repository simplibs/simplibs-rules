"""Tests for the assert_rule_describe function."""

from typing import Any
import pytest
from simplibs.rules.base_class import Rule
from simplibs.rules.testing.asserts.assert_rule_describe import assert_rule_describe


# ----------------------------------------------------------------------
# Dummy Rules for Testing
# ----------------------------------------------------------------------

class _DummyBaseRule(Rule):
    """Shared plumbing: a rule that always passes and keeps the default describe()."""

    __slots__ = ()

    def is_valid(self, value: Any) -> bool:
        return True

    def build_exception(self, value: Any, value_name: str = "value", context: str = ""):
        raise NotImplementedError


class DummyDefaultDescribeRule(_DummyBaseRule):
    """Correct rule that keeps the inherited default description (the class name)."""

    __slots__ = ()


class DummyCustomDescribeRule(_DummyBaseRule):
    """Correct rule with its own description text."""

    __slots__ = ()

    def describe(self) -> str:
        return "> 0"


class DummyEmptyDescribeRule(_DummyBaseRule):
    """Broken rule: describe() returns an empty string."""

    __slots__ = ()

    def describe(self) -> str:
        return ""


class DummyBlankDescribeRule(_DummyBaseRule):
    """Broken rule: describe() returns only whitespace."""

    __slots__ = ()

    def describe(self) -> str:
        return "   "


class DummyNonStringDescribeRule(_DummyBaseRule):
    """Broken rule: describe() returns a non-str value."""

    __slots__ = ()

    def describe(self) -> str:
        return 42  # type: ignore[return-value]


class DummyRaisingDescribeRule(_DummyBaseRule):
    """Broken rule: describe() raises."""

    __slots__ = ()

    def describe(self) -> str:
        raise RuntimeError("describe exploded")


# ----------------------------------------------------------------------
# Tests for assert_rule_describe
# ----------------------------------------------------------------------

def test_assert_rule_describe_default_description_passes(subtests):
    """Verify that the inherited default description satisfies the generic contract."""
    assert_rule_describe(subtests, DummyDefaultDescribeRule())


def test_assert_rule_describe_default_description_matches_class_name(subtests):
    """Verify that the default description can be pinned as the class name."""
    assert_rule_describe(
        subtests,
        DummyDefaultDescribeRule(),
        expected_text="DummyDefaultDescribeRule",
    )


def test_assert_rule_describe_custom_description_passes(subtests):
    """Verify that a custom description passes both generic and exact-text checks."""
    rule = DummyCustomDescribeRule()

    assert_rule_describe(subtests, rule)
    assert_rule_describe(subtests, rule, expected_text="> 0")


def test_assert_rule_describe_type_guard_fails(subtests):
    """Verify fail-fast type guard when rule is not a Rule instance."""
    with pytest.raises(AssertionError, match="expects a Rule instance"):
        assert_rule_describe(
            subtests,
            rule="not_a_rule",  # type: ignore
            verbose=False,
        )


def test_assert_rule_describe_expected_text_mismatch_fails(subtests):
    """Verify failure when the description differs from expected_text."""
    with pytest.raises(AssertionError, match="Expected describe\\(\\) =="):
        assert_rule_describe(
            subtests,
            DummyCustomDescribeRule(),
            expected_text=">= 0",
            verbose=False,
        )


def test_assert_rule_describe_empty_string_fails(subtests):
    """Verify failure when describe() returns an empty string."""
    with pytest.raises(AssertionError, match="non-empty str"):
        assert_rule_describe(subtests, DummyEmptyDescribeRule(), verbose=False)


def test_assert_rule_describe_blank_string_fails(subtests):
    """Verify failure when describe() returns only whitespace."""
    with pytest.raises(AssertionError, match="non-empty str"):
        assert_rule_describe(subtests, DummyBlankDescribeRule(), verbose=False)


def test_assert_rule_describe_non_string_fails(subtests):
    """Verify failure when describe() returns a non-str value."""
    with pytest.raises(AssertionError, match="non-empty str"):
        assert_rule_describe(subtests, DummyNonStringDescribeRule(), verbose=False)


def test_assert_rule_describe_raising_describe_is_not_swallowed(subtests):
    """Verify that an exception raised inside describe() surfaces instead of passing silently."""
    with pytest.raises(RuntimeError, match="describe exploded"):
        assert_rule_describe(subtests, DummyRaisingDescribeRule(), verbose=False)
