import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.containers._helpers.validations import raise_invalid_predicate


@pytest.mark.parametrize(
    "rule, type_name",
    [
        ("text", "str"),
        (5, "int"),
        (None, "NoneType"),
        ([1, 2], "list"),
    ],
    ids=["str", "int", "None", "list"],
)
def test_raise_invalid_predicate_contract(subtests, rule, type_name) -> None:
    """Verify raise_invalid_predicate raises ParamError (wrapping a TypeError) and names the type it got."""

    assert_exception_function(
        subtests,
        raise_invalid_predicate,
        invalid_params=(rule,),
        exception_type=ParamError,
        error_name="INVALID_PREDICATE_TARGET",
        value=type_name,
        exception=TypeError,
        verbose=False,
    )
