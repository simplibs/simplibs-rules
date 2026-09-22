import pytest
# Test tools
from simplibs.exception.testing import (
    assert_exception_function,
    assert_function_valid_input,
)
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_validators import (
    validate_param_is_not_zero,
)


# ---------------------------------------------------------
# 1) Test for happy path
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "rule_name, param_name, value",
    [
        ("DivisibleBy", "divisor", 5),
        ("DivisibleBy", "divisor", -3),
        ("HasRemainder", "divisor", 1.5),
        ("CustomRule", "factor", -0.001),
    ],
)
def test_valid_values(subtests, rule_name, param_name, value) -> None:
    """Test happy path when numeric value is non-zero."""

    assert_function_valid_input(
        subtests,
        validate_param_is_not_zero,
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
            "DivisibleBy",
            "divisor",
            0,
            "non-zero integer",
            "Provide an integer divisor other than zero.",
            "DivisibleBy(divisor=5)",
        ),
        (
            "HasRemainder",
            "divisor",
            0.0,
            "non-zero integer",
            "Provide an integer divisor other than zero.",
            "HasRemainder(divisor=5)",
        ),
        (
            "UnknownRule",
            "param",
            0,
            "non-zero value",
            "Provide a non-zero parameter.",
            "UnknownRule(1)",
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
    """Test that zero values raise ParamError wrapping ValueError."""

    assert_exception_function(
        subtests,
        validate_param_is_not_zero,
        invalid_params=(rule_name, param_name, value),
        exception_type=ParamError,
        error_name="PARAM_CANNOT_BE_ZERO_ERROR",
        label=f"{rule_name}.{param_name}",
        expected=expected,
        value=value,
        problem=f"Parameter '{param_name}' cannot be zero.",
        how_to_fix=(
            fix,
            f"Example: {example}",
        ),
        exception=ValueError,
        verbose=False,
    )