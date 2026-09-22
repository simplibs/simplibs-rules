import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.containers._init_validators import (
    raise_requires_at_least_one_rule_error,
)


@pytest.mark.parametrize(
    "rule_name",
    [
        "AllOf",
        "AnyOf",
        "NoneOf",
    ],
)
def test_raise_requires_at_least_one_rule_error_contract(subtests, rule_name) -> None:
    """Verify that raise_requires_at_least_one_rule_error raises ParamError for empty composite containers."""

    assert_exception_function(
        subtests,
        raise_requires_at_least_one_rule_error,
        invalid_params=(rule_name,),
        exception_type=ParamError,
        error_name="REQUIRES_AT_LEAST_ONE_RULE_ERROR",
        label=f"{rule_name}.*rules",
        expected="at least one rule or predicate argument",
        value=None,
        problem=f"Rule '{rule_name}' requires at least one rule to evaluate.",
        how_to_fix=(
            f"Pass at least one Rule or callable function to '{rule_name}' (e.g., {rule_name}(IsInteger())).",
        ),
        verbose=False,
    )