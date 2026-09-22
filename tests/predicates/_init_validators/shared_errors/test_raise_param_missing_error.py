import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.shared_errors import (
    raise_param_missing_error,
)


@pytest.mark.parametrize(
    "rule_name, key_suffix, expected, fix, example",
    [
        (
            "HasLength",
            "missing",
            "at least one constraint (length, min_length, or max_length)",
            "Provide 'length', 'min_length', or 'max_length' parameter.",
            "HasLength(length=5) or HasLength(min_length=1, max_length=10)",
        ),
        (
            "IsSubclass",
            "missing",
            "at least one type argument",
            "Provide one or more base classes as arguments.",
            "IsSubclass(BaseClass) or IsSubclass(ClassA, ClassB)",
        ),
        (
            "IsInstance",
            "missing",
            "at least one type argument",
            "Provide one or more target types as arguments.",
            "IsInstance(int) or IsInstance(int, float)",
        ),
        (
            "HasKeys",
            "keys",
            "at least one key argument",
            "Provide at least one key to check.",
            "HasKeys('id', 'name')",
        ),
        (
            "CustomRule",
            "missing",
            "at least one required parameter",
            "Provide at least one required parameter for this rule.",
            "CustomRule(...)",
        ),
    ],
)
def test_raise_param_missing_error_contract(
    subtests,
    rule_name,
    key_suffix,
    expected,
    fix,
    example,
) -> None:
    """Verify that raise_param_missing_error raises ParamError wrapping ValueError."""

    assert_exception_function(
        subtests,
        raise_param_missing_error,
        invalid_params=(rule_name, key_suffix),
        exception_type=ParamError,
        error_name="PARAM_MISSING_ERROR",
        label=rule_name,
        expected=expected,
        value=None,
        problem=f"Rule '{rule_name}' requires at least one parameter constraint.",
        how_to_fix=(
            fix,
            f"Example: {example}",
        ),
        exception=ValueError,
        verbose=False,
    )