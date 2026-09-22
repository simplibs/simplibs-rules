import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.rule_errors import (
    raise_user_rule_param_wrong_arity,
)


def sample_func_two_args(a, b):
    return a > b


@pytest.mark.parametrize(
    "rule, callable_desc",
    [
        (lambda: True, "<lambda>"),
        (sample_func_two_args, "sample_func_two_args"),
        ("not_a_callable", "'not_a_callable'"),
    ],
)
def test_raise_user_rule_param_wrong_arity_contract(
    subtests,
    rule,
    callable_desc,
) -> None:
    """Verify that raise_user_rule_param_wrong_arity raises ParamError wrapping ValueError with correct diagnostic details."""
    rule_name = "UserRule"

    assert_exception_function(
        subtests,
        raise_user_rule_param_wrong_arity,
        invalid_params=(rule_name, rule),
        exception_type=ParamError,
        error_name="RULE_PARAM_WRONG_ARITY_ERROR",
        label=f"{rule_name}.rule",
        expected="a callable accepting exactly one positional argument 'value'",
        value=rule,
        problem=(
            f"The callable '{callable_desc}' supplied to '{rule_name}' cannot be called with a single positional value.",
            "It requires zero, multiple mandatory positional arguments, or mandatory keyword-only parameters.",
        ),
        how_to_fix=(
            "Provide a callable that accepts exactly one positional argument to receive the value being validated.",
            f"Example: {rule_name}(lambda v: v > 0)",
            f"Or with default parameters: {rule_name}(lambda v, limit=10: v < limit)",
        ),
        exception=ValueError,
        verbose=False,
    )