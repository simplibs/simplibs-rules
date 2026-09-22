from typing import Annotated, Any, NewType, Optional, TypeVar, Union

from simplibs.rules.predicates.comparisons import GreaterThan
from simplibs.rules.predicates.typing.tools.is_supported_annotation import (
    is_supported_annotation,
)

UserId = NewType("UserId", int)
T = TypeVar("T")


def test_is_supported_annotation_returns_true_for_valid_annotations() -> None:
    """Verify is_supported_annotation returns True for all valid built-in and generic typing shapes."""
    valid_annotations = [
        int,
        str,
        Any,
        type[Any],  # type[Any] is now fully supported
        UserId,
        list[int],
        dict[str, int],
        tuple[int, str],
        Union[int, str],
        Optional[float],
        Annotated[int, GreaterThan(0)],
    ]

    for annotation in valid_annotations:
        assert is_supported_annotation(annotation) is True


def test_is_supported_annotation_returns_false_for_invalid_annotations() -> None:
    """Verify is_supported_annotation returns False for unsupported constructs like TypeVar or forward refs."""
    invalid_annotations = [
        T,  # Raw TypeVar
        "UnparsedForwardRef",  # Plain string / non-type
        type[list[int]],  # Complex generic base is not supported in type[...]
    ]

    for annotation in invalid_annotations:
        assert is_supported_annotation(annotation) is False