import pytest
# Test tools
from simplibs.exception.testing import (
    assert_exception_function,
    assert_function_valid_input,
)
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.containers._init_validators import (
    validate_compose_param_is_callable,
)


# ---------------------------------------------------------
# 1) Test for happy path
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "param_name, value",
    [
        ("transformer", str.strip),
        ("transformer", lambda x: x),
        ("validator", lambda x: True),
        ("validator", str.isalpha),
    ],
)
def test_valid_values(subtests, param_name, value) -> None:
    """Test happy path when value is callable."""

    assert_function_valid_input(
        subtests,
        validate_compose_param_is_callable,
        valid_params=(param_name, value),
        verbose=False,
    )


# ---------------------------------------------------------
# 2) Test for negative path
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "param_name, value, expected, fix, example",
    [
        (
            "transformer",
            "not_callable",
            "callable function or method",
            "Provide a callable object that transforms an input value (e.g., str.strip or custom function).",
            "str.strip",
        ),
        (
            "validator",
            999,
            "Rule instance or callable predicate",
            "Provide a Rule instance or a function returning bool (e.g., HasLength(min_=1)).",
            "HasLength(min_=1)",
        ),
    ],
)
def test_invalid_values(subtests, param_name, value, expected, fix, example) -> None:
    """Test that non-callable parameters raise ParamError."""

    assert_exception_function(
        subtests,
        validate_compose_param_is_callable,
        invalid_params=(param_name, value),
        exception_type=ParamError,
        error_name="COMPOSE_PARAM_NOT_CALLABLE_ERROR",
        label=f"Compose.{param_name}",
        expected=expected,
        value=value,
        problem=f"Parameter '{param_name}' must be callable, but got '{type(value).__name__}'.",
        how_to_fix=(
            fix,
            f"Example: Compose({example}, ...)",
        ),
        verbose=False,
    )