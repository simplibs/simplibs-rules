import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_errors import (
    raise_param_not_container_error,
)


@pytest.mark.parametrize(
    "rule_name, param_name, value, fix, example",
    [
        (
            "IsIn",
            "options",
            123,
            "Provide a container parameter (list, tuple, set, frozenset, dict).",
            "IsIn(['draft', 'published'])",
        ),
        (
            "NotIn",
            "options",
            "not_a_container_instance",
            "Provide a container parameter (list, tuple, set, frozenset, dict).",
            "NotIn(['banned', 'forbidden'])",
        ),
        (
            "IsSubsetOf",
            "reference",
            None,
            "Provide a reference container for subset check.",
            "IsSubsetOf({'admin', 'user'})",
        ),
        (
            "IsSupersetOf",
            "reference",
            12.34,
            "Provide a reference container for superset check.",
            "IsSupersetOf({'read', 'write'})",
        ),
        (
            "CustomRule",
            "items",
            True,
            "Provide a valid container parameter for 'items'.",
            "CustomRule(['value1', 'value2'])",
        ),
    ],
)
def test_raise_param_not_container_error_contract(
    subtests,
    rule_name,
    param_name,
    value,
    fix,
    example,
) -> None:
    """Verify that raise_param_not_container_error raises ParamError wrapping TypeError."""

    assert_exception_function(
        subtests,
        raise_param_not_container_error,
        invalid_params=(rule_name, param_name, value),
        exception_type=ParamError,
        error_name="PARAM_NOT_CONTAINER_ERROR",
        label=f"{rule_name}.{param_name}",
        expected="container (list, tuple, set, frozenset, dict)",
        value=value,
        problem=f"Parameter '{param_name}' must be a container, got '{type(value).__name__}'.",
        how_to_fix=(
            fix,
            f"Example: {example}",
        ),
        exception=TypeError,
        verbose=False,
    )