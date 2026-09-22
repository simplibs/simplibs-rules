import pytest
from simplibs.rules.base_class import Rule
from simplibs.rules.containers._helpers.as_predicate import as_predicate


class DummyRule(Rule):
    """Dummy rule to verify direct method extraction."""

    def is_valid(self, value: object) -> bool:
        return value == "pass"

    def build_exception(
        self,
        value: object,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        return ValueError("Dummy exception")


def test_as_predicate_with_rule_instance() -> None:
    """Verify that as_predicate extracts the bound is_valid method from Rule instances."""
    rule = DummyRule()
    predicate = as_predicate(rule)

    # Check that predicate directly points to the rule's is_valid method
    assert predicate.__func__ is DummyRule.is_valid
    assert predicate("pass") is True
    assert predicate("fail") is False


def test_as_predicate_with_plain_function() -> None:
    """Verify that as_predicate returns plain functions as-is."""

    def custom_fn(val: int) -> bool:
        return val > 0

    predicate = as_predicate(custom_fn)
    assert predicate is custom_fn
    assert predicate(5) is True
    assert predicate(-1) is False


def test_as_predicate_with_lambda() -> None:
    """Verify that as_predicate returns lambdas as-is."""
    is_even = lambda x: x % 2 == 0
    predicate = as_predicate(is_even)

    assert predicate is is_even
    assert predicate(4) is True
    assert predicate(5) is False