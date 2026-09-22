import pytest
from simplibs.exception import ValidationError
from simplibs.rules.base_class import Rule
from simplibs.rules.containers._helpers.build_child_exception import (
    build_child_exception,
)


class DummyChildRule(Rule):
    """Dummy rule providing a custom exception construction."""

    def is_valid(self, value: object) -> bool:
        return False

    def build_exception(
        self,
        value: object,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        label = value_name or "value"
        return RuntimeError(f"Child rule error for {label}={value!r}")


def test_build_child_exception_delegates_to_rule() -> None:
    """Verify that build_child_exception delegates to rule.build_exception for Rule instances."""
    rule = DummyChildRule()
    exc = build_child_exception(rule, "bad_val", value_name="item", context="ctx")

    assert isinstance(exc, RuntimeError)
    assert str(exc) == "Child rule error for item='bad_val'"


def test_build_child_exception_fallback_for_callable() -> None:
    """Verify that build_child_exception uses build_validation_error fallback for plain callables."""

    def custom_predicate(x: int) -> bool:
        return x > 0

    exc = build_child_exception(
        custom_predicate, -5, value_name="num", context="test_context"
    )

    assert isinstance(exc, ValidationError)
    assert exc.label == "num"
    assert exc.context == "test_context"
    assert exc.value == -5