import pytest
# Test tools
from simplibs.exception.testing import (
    assert_exception_function,
    assert_function_valid_input,
)
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_validators import (
    validate_param_remainder_in_range,
)


# ---------------------------------------------------------
# 1) Test for happy path
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "rule_name, divisor, remainder",
    [
        ("HasRemainder", 5, 0),
        ("HasRemainder", 5, 4),
        ("HasRemainder", -5, 2),  # abs(-5) == 5, so 0 <= 2 < 5 is valid
    ],
)
def test_valid_values(subtests, rule_name, divisor, remainder) -> None:
    """Test happy path when remainder is within 0 <= remainder < |divisor|."""

    assert_function_valid_input(
        subtests,
        validate_param_remainder_in_range,
        valid_params=(rule_name, divisor, remainder),
        verbose=False,
    )


# ---------------------------------------------------------
# 2) Test for negative path
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "rule_name, divisor, remainder, problem_msg",
    [
        (
            "HasRemainder",
            5,
            5,  # Upper bound violation
            "Parameter 'remainder' (5) must be between 0 and 4 for divisor 5.",
        ),
        (
            "HasRemainder",
            5,
            -1,  # Lower bound violation
            "Parameter 'remainder' (-1) must be between 0 and 4 for divisor 5.",
        ),
        (
            "HasRemainder",
            -5,
            5,  # abs(-5) == 5 violation
            "Parameter 'remainder' (5) must be between 0 and 4 for divisor -5.",
        ),
    ],
)
def test_invalid_values(subtests, rule_name, divisor, remainder, problem_msg) -> None:
    """Test that remainders out of range raise ParamError wrapping ValueError."""

    assert_exception_function(
        subtests,
        validate_param_remainder_in_range,
        invalid_params=(rule_name, divisor, remainder),
        exception_type=ParamError,
        error_name="REMAINDER_OUT_OF_RANGE_ERROR",
        label=f"{rule_name}.remainder",
        expected=f"0 <= remainder < {abs(divisor)}",
        value=remainder,
        problem=problem_msg,
        how_to_fix=(
            "Ensure remainder is non-negative and strictly less than the absolute value of divisor.",
            "Example: HasRemainder(divisor=5, remainder=2)",
        ),
        exception=ValueError,
        verbose=False,
    )