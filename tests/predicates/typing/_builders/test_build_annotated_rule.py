from typing import Annotated

import pytest

from simplibs.exception import ParamError
from simplibs.rules.containers import AllOf
from simplibs.rules.predicates.comparisons import GreaterThan
from simplibs.rules.predicates.introspection import IsInstance
from simplibs.rules.predicates.logic import UserRule
from simplibs.rules.predicates.typing._builders.build_annotated_rule import (
    build_annotated_rule,
)


def test_build_annotated_rule_with_rule_metadata() -> None:
    """Verify Annotated[int, GreaterThan(0)] combines type check and Rule metadata into AllOf."""
    rule = build_annotated_rule(Annotated[int, GreaterThan(0)])

    # 1. Structural check (the main thing the builder does)
    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], GreaterThan)

    # 2. Quick functional check (without the brittle assert_rule_contract)
    assert rule.is_valid(1) is True
    assert rule.is_valid(100) is True
    assert rule.is_valid(0) is False
    assert rule.is_valid(-10) is False
    assert rule.is_valid("5") is False


def test_build_annotated_rule_with_callable_and_ignored_metadata() -> None:
    """Verify plain callables are wrapped via UserRule and non-predicate metadata is ignored."""
    is_even = lambda x: x % 2 == 0
    # "some description" must be ignored
    rule = build_annotated_rule(Annotated[int, is_even, "some description"])

    # 1. Structural check
    assert isinstance(rule, AllOf)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], IsInstance)
    assert isinstance(rule.rules[1], UserRule)

    # 2. Quick functional check
    assert rule.is_valid(2) is True
    assert rule.is_valid(4) is True
    assert rule.is_valid(1) is False
    assert rule.is_valid("2") is False


def test_build_annotated_rule_without_custom_metadata() -> None:
    """Verify Annotated[int, "only string doc"] unwraps to just IsInstance(int)."""
    # Without any Rule or callable in the metadata, no AllOf may be created!
    rule = build_annotated_rule(Annotated[int, "just docstring"])

    # Must return IsInstance directly, not AllOf
    assert isinstance(rule, IsInstance)
    assert rule.is_valid(42) is True
    assert rule.is_valid("42") is False


def test_build_annotated_rule_callable_exception_means_failure() -> None:
    """Verify an exception raised inside a callable metadata item is a validation failure, not a crash."""
    rule = build_annotated_rule(Annotated[int, lambda x: 1 / x > 0])

    assert rule.is_valid(2) is True
    assert rule.is_valid(0) is False  # ZeroDivisionError inside the callable -> False


def test_build_annotated_rule_callable_with_wrong_arity_raises() -> None:
    """Verify a callable that cannot take exactly one argument is rejected when the rule is built."""
    with pytest.raises(ParamError):
        build_annotated_rule(Annotated[int, lambda: True])
