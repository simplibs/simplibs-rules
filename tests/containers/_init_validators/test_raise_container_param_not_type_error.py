import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ValidationError
from simplibs.rules.containers._init_validators import (
    raise_container_param_not_type_error,
)


@pytest.mark.parametrize(
    "rule_name, param_name, value, expected_type, example_usage, fix_msg",
    [
        (
            "ForEach",
            "rule",
            123,
            "Rule instance or callable",
            "IsInteger()",
            "Pass a valid Rule instance or callable to 'rule'. Example: ForEach(IsInteger())",
        ),
        (
            "Compose",
            "transformer",
            None,
            "callable",
            None,
            "Pass a valid callable to 'transformer'.",
        ),
    ],
)
def test_raise_container_param_not_type_error_contract(
    subtests,
    rule_name,
    param_name,
    value,
    expected_type,
    example_usage,
    fix_msg,
) -> None:
    """Verify that raise_container_param_not_type_error raises a structured ValidationError wrapping TypeError."""

    assert_exception_function(
        subtests,
        raise_container_param_not_type_error,
        invalid_params=(rule_name, param_name, value, expected_type, example_usage),
        exception_type=ValidationError,
        error_name="INVALID_PARAMETER_TYPE",
        label=param_name,
        expected=expected_type,
        value=value,
        problem=(
            f"Parameter '{param_name}' in rule '{rule_name}' must be {expected_type}, "
            f"got '{type(value).__name__}' ({value!r})."
        ),
        context=f"Initialization of rule '{rule_name}'",
        how_to_fix=(fix_msg,),
        exception=TypeError,
        verbose=False,
    )