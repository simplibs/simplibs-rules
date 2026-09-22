import pytest
from simplibs.rules.base_class import Rule
from simplibs.rules.containers._helpers.describe_rule import describe_rule


class CustomNamedRule(Rule):
    """Dummy rule to test class name extraction."""

    def is_valid(self, value: object) -> bool:
        return True

    def build_exception(
        self,
        value: object,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        return ValueError("Error")


class CallableWithoutName:
    """Callable object without a __name__ attribute."""

    def __call__(self, value: object) -> bool:
        return True

    def __repr__(self) -> str:
        return "<CallableWithoutNameRepr>"


def test_describe_rule_with_rule_instance() -> None:
    """Verify describe_rule extracts type(rule).__name__ for Rule instances."""
    rule = CustomNamedRule()
    assert describe_rule(rule) == "CustomNamedRule"


def test_describe_rule_with_named_function() -> None:
    """Verify describe_rule extracts __name__ for standard functions."""

    def my_validation_function(val: object) -> bool:
        return True

    assert describe_rule(my_validation_function) == "my_validation_function"


def test_describe_rule_with_lambda() -> None:
    """Verify describe_rule extracts <lambda> for anonymous functions."""
    anon = lambda x: True
    assert describe_rule(anon) == "<lambda>"


def test_describe_rule_with_unnamed_callable_fallback() -> None:
    """Verify describe_rule falls back to repr(rule) when __name__ is absent."""
    obj = CallableWithoutName()
    assert describe_rule(obj) == "<CallableWithoutNameRepr>"