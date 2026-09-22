from typing import Any, Callable

from simplibs.rules.predicates.introspection import IsCallable
from simplibs.rules.predicates.typing._builders.build_callable_rule import (
    build_callable_rule,
)


def test_build_callable_rule_returns_is_callable() -> None:
    """Verify Callable annotations always unwrap to a plain IsCallable rule regardless of args."""
    # Test plain Callable, Callable with signature, and Callable[..., Any]
    rule_bare = build_callable_rule(Callable)
    rule_full = build_callable_rule(Callable[[int, str], bool])
    rule_dots = build_callable_rule(Callable[..., Any])

    assert isinstance(rule_bare, IsCallable)
    assert isinstance(rule_full, IsCallable)
    assert isinstance(rule_dots, IsCallable)

    # Smoke functional test
    def sample_func(a: int, b: str) -> bool:
        return True

    assert rule_full.is_valid(sample_func) is True
    assert rule_full.is_valid(lambda: None) is True
    assert rule_full.is_valid("not_a_callable") is False