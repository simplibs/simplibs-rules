import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.containers._init_validators import (
    raise_rule_param_not_callable,
)


@pytest.mark.parametrize(
    "rule_name, rule_param, example",
    [
        ("ForEach", "not_callable", "IsInteger()"),
        ("Not", 12345, "IsNone()"),
    ],
)
def test_raise_rule_param_not_callable_contract(
    subtests,
    rule_name,
    rule_param,
    example,
) -> None:
    """Verify that raise_rule_param_not_callable raises ParamError with appropriate contextual fixes."""

    assert_exception_function(
        subtests,
        raise_rule_param_not_callable,
        invalid_params=(rule_name, rule_param),
        exception_type=ParamError,
        error_name="SINGLE_RULE_PARAM_NOT_CALLABLE_ERROR",
        label=f"{rule_name}.rule",
        expected="Rule instance or callable predicate",
        value=rule_param,
        problem=(
            f"Rule '{rule_name}' requires a Rule instance or callable predicate, "
            f"got '{type(rule_param).__name__}'."
        ),
        how_to_fix=(
            f"Provide a valid Rule instance or a function returning bool (e.g., {rule_name}({example})).",
        ),
        verbose=False,
    )