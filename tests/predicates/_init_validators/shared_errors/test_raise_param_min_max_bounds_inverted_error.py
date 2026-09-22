import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_errors import (
    raise_param_min_max_bounds_inverted_error,
)


@pytest.mark.parametrize(
    "rule_name, min_val, max_val, label, expected, problem, fix, example",
    [
        (
            "HasLength",
            10,
            2,
            "HasLength.min_length",
            "min_length <= max_length (min_length=10, max_length=2)",
            "Parameter 'min_length' (10) cannot be greater than 'max_length' (2).",
            "Ensure min_length is less than or equal to max_length.",
            "HasLength(min_length=1, max_length=10)",
        ),
        (
            "InRange",
            100,
            0,
            "InRange.min_val",
            "min_val <= max_val (min_val=100, max_val=0)",
            "Parameter 'min_val' (100) cannot be greater than 'max_val' (0).",
            "Ensure min_val is less than or equal to max_val.",
            "InRange(min_val=1, max_val=10)",
        ),
        (
            "CustomRule",
            50,
            5,
            "CustomRule.min_val",
            "min_val <= max_val (min_val=50, max_val=5)",
            "Parameter 'min_val' (50) cannot be greater than 'max_val' (5).",
            "Ensure minimum boundary is less than or equal to maximum boundary.",
            "CustomRule(min_val=1, max_val=10)",
        ),
    ],
)
def test_raise_param_min_max_bounds_inverted_error_contract(
    subtests,
    rule_name,
    min_val,
    max_val,
    label,
    expected,
    problem,
    fix,
    example,
) -> None:
    """Verify that raise_param_min_max_bounds_inverted_error raises ParamError wrapping ValueError."""

    assert_exception_function(
        subtests,
        raise_param_min_max_bounds_inverted_error,
        invalid_params=(rule_name, min_val, max_val),
        exception_type=ParamError,
        error_name="BOUNDS_INVERTED_ERROR",
        label=label,
        expected=expected,
        value=(min_val, max_val),
        problem=problem,
        how_to_fix=(
            fix,
            f"Example: {example}",
        ),
        exception=ValueError,
        verbose=False,
    )