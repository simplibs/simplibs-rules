import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_errors import (
    raise_param_not_type_error,
)


@pytest.mark.parametrize(
    "rule_name, param_name, value, fix, example",
    [
        (
            "IsSubclass",
            "types",
            "not_a_type",
            "Provide valid class types (objects of type 'type').",
            "IsSubclass(BaseClass)",
        ),
        (
            "IsInstance",
            "types",
            12345,
            "Provide valid class types (objects of type 'type').",
            "IsInstance(int, str)",
        ),
        (
            "CustomRule",
            "cls_type",
            None,
            "Provide a valid class type for 'cls_type'.",
            "CustomRule(MyClass)",
        ),
    ],
)
def test_raise_param_not_type_error_contract(
    subtests,
    rule_name,
    param_name,
    value,
    fix,
    example,
) -> None:
    """Verify that raise_param_not_type_error raises ParamError wrapping TypeError."""

    assert_exception_function(
        subtests,
        raise_param_not_type_error,
        invalid_params=(rule_name, param_name, value),
        exception_type=ParamError,
        error_name="PARAM_NOT_TYPE_ERROR",
        label=f"{rule_name}.{param_name}",
        expected="type (class)",
        value=value,
        problem=f"Parameter '{param_name}' must be a type (class), got '{type(value).__name__}'.",
        how_to_fix=(
            fix,
            f"Example: {example}",
        ),
        exception=TypeError,
        verbose=False,
    )