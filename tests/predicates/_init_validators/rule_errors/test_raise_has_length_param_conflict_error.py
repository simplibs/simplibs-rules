import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.rule_errors import (
    raise_has_length_param_conflict_error,
)


@pytest.mark.parametrize(
    "length, min_length, max_length, problem_msg",
    [
        (
            5,
            1,
            None,
            "Parameter 'length' (5) cannot be combined with 'min_length'.",
        ),
        (
            5,
            None,
            10,
            "Parameter 'length' (5) cannot be combined with 'max_length'.",
        ),
        (
            5,
            1,
            10,
            "Parameter 'length' (5) cannot be combined with 'min_length' and 'max_length'.",
        ),
    ],
)
def test_raise_has_length_param_conflict_error_contract(
    subtests,
    length,
    min_length,
    max_length,
    problem_msg,
) -> None:
    """Verify that raise_has_length_param_conflict_error raises ParamError wrapping ValueError for parameter conflicts."""

    assert_exception_function(
        subtests,
        raise_has_length_param_conflict_error,
        invalid_params=(length, min_length, max_length),
        exception_type=ParamError,
        error_name="PARAM_CONFLICT_ERROR",
        label="HasLength.length",
        expected="either 'length' or 'min_length'/'max_length', not both",
        value={"length": length, "min_length": min_length, "max_length": max_length},
        problem=problem_msg,
        how_to_fix=(
            "Specify either 'length' for exact match OR 'min_length'/'max_length' for a range, do not mix them.",
            "Example: HasLength(length=5) OR HasLength(min_length=1, max_length=10)",
        ),
        exception=ValueError,
        verbose=False,
    )