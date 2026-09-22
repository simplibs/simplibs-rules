"""Tests for the UserRule rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.exception import ValidationError
from simplibs.rules.predicates.logic import UserRule
from simplibs.rules.testing import assert_rule_contract


def positive_pred(x: int) -> bool:
    return x > 0


def test_user_rule_contract(subtests):
    """Verify the complete contract of UserRule."""
    rule = UserRule(positive_pred)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 10, 100],
        invalid_values=[0, -5, "not_an_int"],  # String triggers exception inside lambda, treated as False
        invalid_init_params=[
            (("not_callable",), {}),  # String is not callable -> ParamError
            ((lambda: True,), {}),     # Zero-arg function wrong arity -> ParamError
            ((lambda a, b: a + b,), {}),  # Two-arg function wrong arity -> ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_user_rule_swallows_exceptions_in_is_valid():
    """Verify that exceptions raised inside user callable are caught and return False."""

    def raising_predicate(x):
        raise ValueError("Something went wrong inside predicate")

    rule = UserRule(raising_predicate)

    # Must return False, not raise ValueError
    assert rule.is_valid(10) is False


def test_user_rule_exception(subtests):
    """Verify diagnosis (ValueError) when callable condition fails."""
    rule = UserRule(positive_pred)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(-5, Kwargs(value_name="score")),
        exception_type=ValidationError,
        label="score",
        value=-5,
        error_name="USER_RULE_ERROR",
        expected="value satisfying callable condition 'positive_pred'",
        problem="Value failed (or raised inside) callable 'positive_pred'.",
        how_to_fix="Provide a value accepted by 'positive_pred'.",
        exception=ValueError,
        verbose=False,
    )