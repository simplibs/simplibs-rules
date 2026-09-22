import re
import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates._init_validators.rule_errors import (
    raise_regex_param_invalid_pattern_error,
)


@pytest.mark.parametrize(
    "pattern, err",
    [
        ("[a-z", re.error("unterminated character set at position 0")),
        ("*invalid", re.error("nothing to repeat at position 0")),
        ("(", re.error("missing ), unterminated subpattern at position 0")),
    ],
)
def test_raise_regex_param_invalid_pattern_error_contract(
    subtests,
    pattern,
    err,
) -> None:
    """Verify that raise_regex_param_invalid_pattern_error raises ParamError wrapping ValueError with regex engine diagnostics."""

    assert_exception_function(
        subtests,
        raise_regex_param_invalid_pattern_error,
        invalid_params=(pattern, err),
        exception_type=ParamError,
        error_name="INVALID_REGEX_PATTERN_ERROR",
        label="Regex.pattern",
        expected="valid regular expression syntax",
        value=pattern,
        problem=f"Invalid regex pattern /{pattern}/: {err}.",
        how_to_fix=(
            "Provide a syntactically correct regular expression pattern.",
            "Example: Regex(r'^[a-z]+$')",
        ),
        exception=ValueError,
        verbose=False,
    )