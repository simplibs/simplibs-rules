import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_errors import (
    raise_param_not_non_negative_integer_error,
)


@pytest.mark.parametrize(
    "rule_name, param_name, value, expected_desc, problem_desc, exc_type, fix, example",
    [
        # Type mismatch scenarios (TypeError)
        (
            "HasLength",
            "length",
            "5",
            "non-negative integer (int)",
            "Parameter 'length' must be an integer, got 'str'.",
            TypeError,
            "Provide a non-negative integer for exact length match.",
            "HasLength(length=5)",
        ),
        (
            "HasLength",
            "min_length",
            True,  # Booleans are rejected as non-integers
            "non-negative integer (int)",
            "Parameter 'min_length' must be an integer, got 'bool'.",
            TypeError,
            "Provide a non-negative integer for minimum length boundary.",
            "HasLength(min_length=1)",
        ),
        # Value boundary scenarios (ValueError)
        (
            "HasLength",
            "max_length",
            -1,
            "integer greater than or equal to 0",
            "Parameter 'max_length' must be non-negative (>= 0), got -1.",
            ValueError,
            "Provide a non-negative integer for maximum length boundary.",
            "HasLength(max_length=10)",
        ),
        (
            "IsPi",
            "decimal_places",
            -5,
            "integer greater than or equal to 0",
            "Parameter 'decimal_places' must be non-negative (>= 0), got -5.",
            ValueError,
            "Provide a non-negative integer for decimal places precision.",
            "IsPi(decimal_places=5)",
        ),
        (
            "CustomRule",
            "param",
            "invalid",
            "non-negative integer (int)",
            "Parameter 'param' must be an integer, got 'str'.",
            TypeError,
            "Provide a valid non-negative integer for 'param'.",
            "CustomRule(param=5)",
        ),
    ],
)
def test_raise_param_not_non_negative_integer_error_contract(
    subtests,
    rule_name,
    param_name,
    value,
    expected_desc,
    problem_desc,
    exc_type,
    fix,
    example,
) -> None:
    """Verify that raise_param_not_non_negative_integer_error raises ParamError with appropriate inner exception."""

    assert_exception_function(
        subtests,
        raise_param_not_non_negative_integer_error,
        invalid_params=(rule_name, param_name, value),
        exception_type=ParamError,
        error_name="PARAM_NOT_NON_NEGATIVE_INT_ERROR",
        label=f"{rule_name}.{param_name}",
        expected=expected_desc,
        value=value,
        problem=problem_desc,
        how_to_fix=(
            fix,
            f"Example: {example}",
        ),
        exception=exc_type,
        verbose=False,
    )