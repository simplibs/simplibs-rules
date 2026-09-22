from typing import Any, get_origin
# Outers
from ...base_class import Rule
from ...predicates.introspection import IsInstance
# Inners
from .IsAny import _IS_ANY
from ._builders import ORIGIN_TABLE
from ._validations import raise_unsupported_annotation_error


def build_typing_rule(annotation: Any) -> Rule:
    """Recursively decompose a typing annotation into a single Rule.

    This is the single recursive entry point IsTyping and every builder
    call back into for nested annotation slots (a list's item type, a
    dict's value type, a Union member, ...).

    Args:
        annotation: A plain class, a direct Rule instance, or a supported typing construct
            (Any, Annotated, Union/|, Literal, Type, Callable, or a
            list/set/dict/tuple/Iterable/Sequence/Mapping/... generic).

    Returns:
        A single Rule instance equivalent to the given annotation.

    Raises:
        ParamError: If the annotation (or any nested fragment of it) is
            not a recognized type or typing construct.
    """

    # 1. Any process — unconstrained, checked first as it has no origin
    if annotation is Any:
        return _IS_ANY

    # 2. Extract origin construct
    origin = get_origin(annotation)

    # 3. No origin — direct Rule, concrete class, NewType, or unsupported
    if origin is None:

        # 3.1 Direct Rule instance (e.g. GreaterThan(0) used directly as annotation)
        if isinstance(annotation, Rule):
            return annotation

        # 3.2 Plain class types (e.g. int, str, CustomClass)
        if isinstance(annotation, type):
            return IsInstance(annotation)

        # 3.3 NewType unwrap guard (e.g. NewType("UserId", int))
        if hasattr(annotation, "__supertype__"):
            return build_typing_rule(annotation.__supertype__)

        # 3.4 Unsupported non-type annotation (e.g. raw TypeVar, ForwardRef, or invalid object)
        raise_unsupported_annotation_error(annotation)

    # 4. Origin lookup in registry
    builder = ORIGIN_TABLE.get(origin)

    # 5. Unsupported origin construct
    if builder is None:
        raise_unsupported_annotation_error(annotation)

    # 6. Delegate rule construction to specialized builder
    return builder(annotation)


_DESIGN_NOTES = """
# _dispatch — IsTyping's Recursive Decomposition Engine

## Purpose
The single function every annotation — top-level or nested — passes
through exactly once per recursion level. It handles primitives directly
(like `Any`, direct `Rule` instances, or plain `type` objects) and routes
all generic/structured type constructs through `ORIGIN_TABLE`.

---

## 1. Clean Evaluation Pipeline

The dispatch order follows a minimal, strict logic path:

1. **`Any`** — Has no origin and is not a `type` instance; returns the
   `_IS_ANY` singleton directly.
2. **No Origin (`origin is None`)** — Pass-through for direct `Rule` instances,
   handles concrete class types via `IsInstance(annotation)`, unwraps `NewType`
   wrappers recursively, or raises an error for unsupported non-type constructs.
3. **Table Lookup (`ORIGIN_TABLE`)** — Every structured origin (including
   `tuple` and `Annotated` in Python 3.11+) maps directly to its
   specialized builder function.

---

## 2. No-Origin Branch Logic (`origin is None`)

This branch explicitly handles constructs where `get_origin(annotation)` returns `None`:

* **`isinstance(annotation, Rule)` (3.1):** First-class Rule pass-through. If an annotation
  is already a `Rule` instance, no decomposition is needed — it is returned as-is.
* **`isinstance(annotation, type)` (3.2):** High-frequency fast path. Standard class
  types (`int`, `str`, custom domain classes) are `type` instances and directly emit `IsInstance`.
* **`hasattr(annotation, "__supertype__")` (3.3):** In Python 3.11+, `NewType` creates a unique
  wrapper object (not a `type` instance, and with `origin is None`). It stores its underlying type
  in `__supertype__`. We recursively re-enter `build_typing_rule` with the underlying type
  (e.g., `NewType("UserId", int)` unwraps to `int`).
* **Fallback (`raise_unsupported_annotation_error`) (3.4):** Handles unprocessable non-type structures
  without origins, such as bare `TypeVar` (e.g., `T = TypeVar("T")`) or unparsed `ForwardRef` strings,
  raising a clear error.

### Why `Annotated` Metadata Fallback is Omitted
In older Python versions (pre-3.10), `Annotated` sometimes required a fallback inspection via
`hasattr(annotation, "__metadata__")`. Because this library targets **Python 3.11+**, `get_origin(Annotated[...])`
is guaranteed by the standard library to strictly return `typing.Annotated`. Therefore, checking `__metadata__` in
the `origin is None` branch is redundant dead code and deliberately excluded.

---

## 3. Stateless Module-Level Singleton

`_IS_ANY` is instantiated once at module import time and reused across
all `Any` occurrences.

---

## 4. Delegation of Complex Origin Logic

Complex constructs such as heterogeneous vs. homogeneous `tuple` shapes or
`Annotated` metadata extraction do not contaminate the main dispatcher
branching. Their respective builder functions (`build_tuple_rule` and
`build_annotated_rule`) encapsulate their own internal inspection logic
when invoked via `ORIGIN_TABLE`.
"""