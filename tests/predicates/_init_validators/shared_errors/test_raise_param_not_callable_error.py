import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_errors import (
    raise_param_not_callable_error,
)


@pytest.mark.parametrize(
    "rule_name, param_name, value, expected_type_name",
    [
        ("UserRule", "rule", 123, "int"),
        ("UserRule", "rule", "invalid", "str"),
        ("UserRule", "rule", None, "NoneType"),
        ("CustomRule", "predicate", [1, 2, 3], "list"),
    ],
)
def test_raise_param_not_callable_error_contract(
    subtests,
    rule_name,
    param_name,
    value,
    expected_type_name,
) -> None:
    """Verify that raise_param_not_callable_error raises ParamError wrapping ValueError with accurate type diagnostics."""

    assert_exception_function(
        subtests,
        raise_param_not_callable_error,
        invalid_params=(rule_name, param_name, value),
        exception_type=ParamError,
        error_name="PARAM_NOT_CALLABLE_ERROR",
        label=f"{rule_name}.{param_name}",
        expected="a callable object (function, lambda, or predicate)",
        value=value,
        problem=(
            f"Parameter '{param_name}' of '{rule_name}' must be a callable, "
            f"got '{expected_type_name}'."
        ),
        how_to_fix=(
            f"Provide a valid function or lambda to '{rule_name}'.",
            f"Example: {rule_name}(lambda v: v > 0)",
        ),
        exception=ValueError,
        verbose=False,
    )