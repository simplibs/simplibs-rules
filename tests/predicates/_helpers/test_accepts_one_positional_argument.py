import pytest
from simplibs.rules.predicates._helpers.accepts_one_positional_argument import (
    accepts_one_positional_argument,
)


def test_accepts_one_positional_argument_valid_single_arg() -> None:
    """Verify single-argument callables are accepted."""

    def single_arg(x):
        return x > 0

    assert accepts_one_positional_argument(single_arg) is True
    assert accepts_one_positional_argument(lambda x: True) is True


def test_accepts_one_positional_argument_valid_optional_extra_args() -> None:
    """Verify callables with extra positional or keyword arguments with defaults are accepted."""

    def extra_defaults(a, b=10, *, c=True):
        return True

    assert accepts_one_positional_argument(extra_defaults) is True


def test_accepts_one_positional_argument_valid_var_positional() -> None:
    """Verify callables accepting *args are accepted."""

    def var_args(*args):
        return True

    assert accepts_one_positional_argument(var_args) is True


def test_accepts_one_positional_argument_invalid_missing_positional() -> None:
    """Verify callables requiring zero arguments are rejected."""

    def no_args():
        return True

    assert accepts_one_positional_argument(no_args) is False


def test_accepts_one_positional_argument_invalid_mandatory_second_arg() -> None:
    """Verify callables requiring two or more positional arguments without defaults are rejected."""

    def two_mandatory(a, b):
        return True

    assert accepts_one_positional_argument(two_mandatory) is False
    assert accepts_one_positional_argument(lambda x, y: True) is False


def test_accepts_one_positional_argument_invalid_mandatory_keyword_only() -> None:
    """Verify callables requiring a keyword-only argument (even with *args) are rejected."""

    def mandatory_kw_only(a, *, key):
        return True

    def var_args_with_mandatory_kw(*args, key):
        return True

    assert accepts_one_positional_argument(mandatory_kw_only) is False
    assert accepts_one_positional_argument(var_args_with_mandatory_kw) is False


def test_accepts_one_positional_argument_uninspectable_builtin() -> None:
    """Verify uninspectable callables (e.g., C builtins) default to True."""
    # len accepts 1 argument, but inspect.signature fails on some C builtins
    assert accepts_one_positional_argument(abs) is True