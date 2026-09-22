import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.exception import ParamError
from simplibs.rules.predicates.typing._validations import (
    raise_unsupported_annotation_error,
)


class CustomUnsupportedClass:
    """Mock unsupported class for testing."""


@pytest.mark.parametrize(
    "annotation",
    [
        CustomUnsupportedClass(),
        "UnresolvedForwardRef",
        12345,
    ],
)
def test_raise_unsupported_annotation_error_contract(subtests, annotation) -> None:
    """Verify raise_unsupported_annotation_error produces a well-formed ParamError card."""

    def raising_wrapper(unsupported_annotation):
        raise_unsupported_annotation_error(unsupported_annotation)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(annotation,),
        exception_type=ParamError,
        error_name="UNSUPPORTED_TYPING_ANNOTATION_ERROR",
        label="annotation",
        expected="A supported type or typing annotation",
        value=annotation,
        problem=f"Annotation {annotation!r} is not a recognized type or typing construct.",
        how_to_fix=(
            "Use a plain class (e.g. int, str, CustomClass).",
            "Use standard generics (list[T], set[T], dict[K, V], tuple[...]).",
            "Use special typing constructs (Union / |, Optional, Literal, Annotated).",
            "Use Callable, Type, NewType, or Any.",
            "If using ForwardRef or complex type aliases, resolve them to concrete types first.",
        ),
        verbose=False,
    )