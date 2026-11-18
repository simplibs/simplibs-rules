"""
Tests for assert_rule_contract — invalid_init_params must never be skipped silently by deep_check=False.
"""
from typing import Any

import pytest

from simplibs.exception import ParamError, ValidationError
from simplibs.rules.base_class import Rule
from simplibs.rules.testing.assert_rule_contract import assert_rule_contract


class LimitRule(Rule):
    """Fully valid rule: an integer not above `limit`."""

    __slots__ = ("limit",)

    def __init__(self, limit: int = 10):
        if limit <= 0:
            raise ParamError("limit must be positive")
        self.limit = limit

    def is_valid(self, value: Any) -> bool:
        return isinstance(value, int) and value <= self.limit

    def build_exception(self, value: Any, value_name: str = "value", context: str = "") -> ValidationError:
        return ValidationError(
            problem="Value exceeds limit or is not int.",
            expected=f"Integer <= {self.limit}",
            how_to_fix="Provide a smaller integer.",
            label=value_name,
            value=value,
            context=context,
            error_name="LIMIT_ERROR",
        )

    def describe(self) -> str:
        return f"integer <= {self.limit}"


def test_assert_rule_contract_fails_on_init_params_with_deep_check_false(subtests):
    """Verify the ParamError sweep is never silently skipped by deep_check=False."""
    with pytest.raises(AssertionError, match="deep_check=False"):
        assert_rule_contract(
            subtests,
            rule=LimitRule(limit=10),
            valid_values=[1],
            invalid_values=[11],
            rule_factory=LimitRule,
            invalid_init_params=[((-5,), {})],
            deep_check=False,
            verbose=False,
        )


def test_assert_rule_contract_deep_check_false_without_init_params_still_passes(subtests):
    """Verify that deep_check=False alone stays valid: only the combination with init params is a mistake."""
    assert_rule_contract(
        subtests,
        rule=LimitRule(limit=10),
        valid_values=[1],
        invalid_values=[11],
        deep_check=False,
        verbose=False,
    )
