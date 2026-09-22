"""Tests for the EndsWith rule."""

import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import EndsWith


def test_ends_with_contract(subtests):
    """Verify the complete contract of the EndsWith rule."""
    rule = EndsWith(".py")

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=["script.py", "test_file.py", ".py"],
        invalid_values=["script.pyc", "script.py.bak", "script.txt", "", 123, None, True],
        invalid_init_params=[
            ((123,), {}),       # Non-string suffix -> ParamError
            ((None,), {}),      # None suffix -> ParamError
            ((True,), {}),      # Boolean suffix -> ParamError
            (([],), {}),        # List suffix -> ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_ends_with_exception_type_error(subtests):
    """Verify diagnosis (TypeError) when input value is not a string."""
    rule = EndsWith(".py")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(None, Kwargs(value_name="filename")),
        exception_type=ValidationError,
        label="filename",
        value=None,
        error_name="ENDS_WITH_ERROR",
        expected="string ending with '.py'",
        problem="Value None of type 'NoneType' is not a string.",
        how_to_fix="Provide a string value.",
        exception=TypeError,
        verbose=False,
    )


def test_ends_with_exception_value_error(subtests):
    """Verify diagnosis (ValueError) when string does not end with the required suffix."""
    rule = EndsWith(".py")

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("document.txt", Kwargs(value_name="filename")),
        exception_type=ValidationError,
        label="filename",
        value="document.txt",
        error_name="ENDS_WITH_ERROR",
        expected="string ending with '.py'",
        problem="Value 'document.txt' does not end with '.py'.",
        how_to_fix="Provide a string ending with '.py'.",
        exception=ValueError,
        verbose=False,
    )