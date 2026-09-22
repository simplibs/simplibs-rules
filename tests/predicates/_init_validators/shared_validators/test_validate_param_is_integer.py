import pytest
# Test tools
from simplibs.exception.testing import (
    assert_exception_function,
    assert_function_valid_input,
)
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_validators import (
    validate_param_is_integer,
)


# ---------------------------------------------------------
# 1) Test for happy path
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "rule_name, param_name, value",
    [
        ("DivisibleBy", "divisor", 5),
        ("DivisibleBy", "divisor", -10),
        ("HasRemainder", "remainder", 0),
        ("CustomRule", "limit", 100),
    ],
)
def test_valid_values(subtests, rule_name, param_name, value) -> None:
    """Test happy path when value is strictly an integer."""

    assert_function_valid_input(
        subtests,
        validate_param_is_integer,
        valid_params=(rule_name, param_name, value),
        verbose=False,
    )


# ---------------------------------------------------------
# 2) Test for negative path
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "rule_name, param_name, value, fix, example",
    [
        (
            "DivisibleBy",
            "divisor",
            5.5,
            "Provide an non-zero integer divisor.",
            "DivisibleBy(divisor=5)",
        ),
        (
            "HasRemainder",
            "divisor",
            True,  # Booleans must be rejected
            "Provide an non-zero integer divisor.",
            "DivisibleBy(divisor=5)",
        ),
        (
            "HasRemainder",
            "remainder",
            "3",
            "Provide an integer remainder.",
            "HasRemainder(divisor=5, remainder=2)",
        ),
        (
            "UnknownRule",
            "custom_param",
            None,
            "Provide an integer value (booleans are excluded).",
            "UnknownRule(5)",
        ),
    ],
)
def test_invalid_values(subtests, rule_name, param_name, value, fix, example) -> None:
    """Test that non-integer values or booleans raise ParamError wrapping TypeError."""

    assert_exception_function(
        subtests,
        validate_param_is_integer,
        invalid_params=(rule_name, param_name, value),
        exception_type=ParamError,
        error_name="PARAM_NOT_TYPE_ERROR",
        label=f"{rule_name}.{param_name}",
        expected="non-zero integer",
        value=value,
        problem=f"Parameter '{param_name}' must be an int, got '{type(value).__name__}'.",
        how_to_fix=(
            fix,
            f"Example: {example}",
        ),
        exception=TypeError,
        verbose=False,
    )