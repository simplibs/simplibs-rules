from typing import Any
# Outers
from .._builders.ORIGIN_TABLE import ORIGIN_TABLE


def get_supported_origins() -> frozenset[Any]:
    """Return an immutable set of all supported typing origin constructs.

    This includes standard generic origins (list, set, dict, tuple),
    special typing constructs (Union, Optional, Literal, Callable, Type, Annotated),
    and typing equivalents from the typing module.

    Returns:
        A frozenset containing all supported typing origin keys.
    """
    return frozenset(ORIGIN_TABLE.keys())


_DESIGN_NOTES = """
# get_supported_origins — Supported Origins Inspector

## Purpose
A public inspection utility that exposes an immutable set of all type origin
constructs supported by the `simplibs.validate` typing engine.

---

## 1. Immutable Reflection & Performance

Returns a `frozenset` constructed directly from `ORIGIN_TABLE.keys()`. This
prevents external callers from mutating the internal registry while providing
$O(1)$ set-membership lookups for runtime environment inspection.

---

## 2. Introspection Support

Enables external tools, CLI diagnostics, and developer utilities to easily
discover which standard library generic containers, ABCs, and `typing`
module constructs (such as `list`, `Union`, `Literal`, `Callable`, or
`Annotated`) can be compiled into rules by the validation engine.
"""