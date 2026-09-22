import pytest
# Test tools
from simplibs.exception.testing import (
    assert_exception_function,
    assert_function_valid_input,
)
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_validators import (
    validate_param_is_primitive_number,
)


# ---------------------------------------------------------
# 1) Test for happy path
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "rule_name, param_name, value",
    [
        ("CloseTo", "target", 10.0),
        ("CloseTo", "target", 5),
        ("CloseTo", "rel_tol", 1e-3),
        ("CloseTo", "abs_tol", 0),
    ],
)
def test_valid_values(subtests, rule_name, param_name, value) -> None:
    """Test happy path when value is a primitive int or float."""

    assert_function_valid_input(
        subtests,
        validate_param_is_primitive_number,
        valid_params=(rule_name, param_name, value),
        verbose=False,
    )


# ---------------------------------------------------------
# 2) Test for negative path
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "rule_name, param_name, value, expected, fix, example",
    [
        (
            "CloseTo",
            "target",
            "10.0",
            "primitive number (int or float)",
            "Provide a primitive target number (int or float).",
            "CloseTo(10.0, rel_tol=1e-3)",
        ),
        (
            "CloseTo",
            "rel_tol",
            True,  # Booleans must be rejected
            "primitive number (int or float)",
            "Provide a relative tolerance value (int or float).",
            "CloseTo(10.0, rel_tol=1e-3)",
        ),
        (
            "CloseTo",
            "abs_tol",
            None,
            "primitive number (int or float)",
            "Provide an absolute tolerance value (int or float).",
            "CloseTo(10.0, abs_tol=0.5)",
        ),
        (
            "UnknownRule",
            "param",
            [1, 2],
            "int or float",
            "Provide a primitive number (int or float; booleans excluded).",
            "UnknownRule(10.5)",
        ),
    ],
)
def test_invalid_values(
    subtests,
    rule_name,
    param_name,
    value,
    expected,
    fix,
    example,
) -> None:
    """Test that non-numeric types or booleans raise ParamError wrapping TypeError."""

    assert_exception_function(
        subtests,
        validate_param_is_primitive_number,
        invalid_params=(rule_name, param_name, value),
        exception_type=ParamError,
        error_name="PARAM_NOT_TYPE_ERROR",
        label=f"{rule_name}.{param_name}",
        expected=expected,
        value=value,
        problem=f"Parameter '{param_name}' must be a primitive number (int or float), got '{type(value).__name__}'.",
        how_to_fix=(
            fix,
            f"Example: {example}",
        ),
        exception=TypeError,
        verbose=False,
    )