import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_errors import (
    raise_param_not_string_error,
)


@pytest.mark.parametrize(
    "rule_name, param_name, value, fix, example",
    [
        (
            "StartsWith",
            "prefix",
            123,
            "Provide a string prefix parameter.",
            "StartsWith('https://')",
        ),
        (
            "EndsWith",
            "suffix",
            [".py"],
            "Provide a string suffix parameter.",
            "EndsWith('.py')",
        ),
        (
            "Contains",
            "substring",
            None,
            "Provide a string substring parameter.",
            "Contains('@')",
        ),
        (
            "Regex",
            "pattern",
            10101,
            "Provide a valid regex string pattern.",
            "Regex(r'^[a-z]+$')",
        ),
        (
            "HasAttribute",
            "attr_name",
            True,
            "Provide a string attribute name parameter.",
            "HasAttribute('append')",
        ),
        (
            "CustomRule",
            "text",
            {"key": "val"},
            "Provide a string for 'text'.",
            "CustomRule(text='...')",
        ),
    ],
)
def test_raise_param_not_string_error_contract(
    subtests,
    rule_name,
    param_name,
    value,
    fix,
    example,
) -> None:
    """Verify that raise_param_not_string_error raises ParamError wrapping TypeError."""

    assert_exception_function(
        subtests,
        raise_param_not_string_error,
        invalid_params=(rule_name, param_name, value),
        exception_type=ParamError,
        error_name="PARAM_NOT_TYPE_ERROR",
        label=f"{rule_name}.{param_name}",
        expected="string",
        value=value,
        problem=f"Parameter '{param_name}' must be a str, got '{type(value).__name__}'.",
        how_to_fix=(
            fix,
            f"Example: {example}",
        ),
        exception=TypeError,
        verbose=False,
    )