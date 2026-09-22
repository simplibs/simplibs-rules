from collections import abc as collections_abc
import typing

from simplibs.rules.predicates.typing.tools.get_supported_origins import (
    get_supported_origins,
)


def test_get_supported_origins_returns_frozenset() -> None:
    """Verify get_supported_origins returns an immutable frozenset containing expected origins."""
    origins = get_supported_origins()

    assert isinstance(origins, frozenset)
    assert len(origins) > 0

    # Smoke check klíčových typů
    assert list in origins
    assert dict in origins
    assert typing.Union in origins
    assert typing.Annotated in origins
    assert collections_abc.Iterable in origins