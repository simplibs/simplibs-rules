import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_errors import (
    raise_param_min_max_incomparable_error,
)


@pytest.mark.parametrize(
    "rule_name, min_val, max_val, label, min_label, max_label, example",
    [
        (
            "InRange",
            1,
            "10",
            "InRange.min_val/max_val",
            "min_val",
            "max_val",
            "InRange(min_val=1, max_val=10)",
        ),
        (
            "CustomRule",
            [1, 2],
            5,
            "CustomRule.min_val/max_val",
            "min_val",
            "max_val",
            "CustomRule(1, 10)",
        ),
    ],
)
def test_raise_param_min_max_incomparable_error_contract(
    subtests,
    rule_name,
    min_val,
    max_val,
    label,
    min_label,
    max_label,
    example,
) -> None:
    """Verify that raise_param_min_max_incomparable_error raises ParamError wrapping TypeError."""

    assert_exception_function(
        subtests,
        raise_param_min_max_incomparable_error,
        invalid_params=(rule_name, min_val, max_val),
        exception_type=ParamError,
        error_name="INCOMPARABLE_RANGE_BOUNDS_ERROR",
        label=label,
        expected="comparable boundary types",
        value=(min_val, max_val),
        problem=f"Cannot compare boundary types '{type(min_val).__name__}' ({min_val!r}) and '{type(max_val).__name__}' ({max_val!r}).",
        how_to_fix=(
            f"Provide '{min_label}' and '{max_label}' of comparable types.",
            f"Example: {example}",
        ),
        exception=TypeError,
        verbose=False,
    )