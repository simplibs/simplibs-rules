"""Tests for the raise_invalid core function."""

import pytest
from simplibs.exception import ValidationError
from simplibs.rules.tools.raise_invalid import raise_invalid
from simplibs.rules.base_class import Rule


class DummyRuleWithSpy(Rule):
    """Dummy rule to verify that is_valid is never invoked."""

    def __init__(self) -> None:
        self.is_valid_called = False

    def is_valid(self, value: object) -> bool:
        self.is_valid_called = True
        return True

    def build_exception(
        self,
        value: object,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        label = value_name or "value"
        return RuntimeError(f"Unconditional trigger for {label} with value {value!r}")


def test_raise_invalid_bypasses_rule_evaluation() -> None:
    """Verify raise_invalid never invokes rule.is_valid() or rule.__call__()."""
    rule = DummyRuleWithSpy()

    with pytest.raises(RuntimeError, match="Unconditional trigger for target_var with value 'test'"):
        raise_invalid("test", rule, value_name="target_var")

    assert rule.is_valid_called is False, "raise_invalid must not evaluate rule.is_valid()"


def test_raise_invalid_with_callable_raises_validate_error() -> None:
    """Verify raise_invalid with plain callable constructs and raises ValidationError."""
    called = False

    def dummy_fn(x: object) -> bool:
        nonlocal called
        called = True
        return True

    with pytest.raises(ValidationError) as exc_info:
        raise_invalid("bad_val", dummy_fn, value_name="val_name", context="ctx_info")

    assert called is False, "raise_invalid must not execute the callable predicate"
    err = exc_info.value
    assert err.label == "val_name"
    assert err.context == "ctx_info"
    assert err.value == "bad_val"