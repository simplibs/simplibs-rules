from typing import Any, get_args, get_origin
# Outers
from ....base_class import Rule
from ....containers import AllOf, ForEach
from ....predicates.introspection import IsInstance


def build_elements_rule(annotation: Any, *, container_type: type | None = None) -> Rule:
    """ELEMENTS process: container type check + one rule applied to every item.

    Covers any generic where "is this the right container, and does every
    item satisfy one shared item rule" fully describes the annotation:
    list[T], set[T], frozenset[T], Iterable[T], Sequence[T], Collection[T],
    and homogeneous tuple[T, ...] (via the explicit container_type override
    — see section 2 of the design notes below).

    Args:
        annotation: The full generic annotation (e.g. `list[int]`).
        container_type: Overrides the container type used for the
            IsInstance check. Needed for `tuple[T, ...]`, where the real
            runtime container is `tuple` but the annotation's own origin
            handling in the dispatcher already branched on `args` before
            reaching here — see IsTyping's design notes.

    Returns:
        A single Rule — IsInstance(container) alone if the annotation has
        no type arguments (e.g. bare `list`), otherwise an AllOf adding
        ForEach(item_rule).
    """

    # 1. Recursive build_typing_rule import — deferred, see elements_builder's notes
    from ..build_typing_rule import build_typing_rule

    # 2. Determine the concrete container type for the IsInstance check
    origin = container_type or get_origin(annotation)

    # 3. Base container check
    parts: list[Rule] = [IsInstance(origin)]

    # 4. Per-item rule, if the annotation specifies an item type
    args = get_args(annotation)
    if args:
        item_rule = build_typing_rule(args[0])
        parts.append(ForEach(item_rule))

    # 5. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# elements_builder — ELEMENTS Process

## Purpose
The "container + rule per item" process — the single largest group of
typing constructs this library needs to support, precisely because
`list[T]`, `set[T]`, `Iterable[T]`, `Sequence[T]`, and `Collection[T]` all
reduce to the exact same two checks: is this the right kind of container,
and does every item satisfy one shared item rule.

---

## 1. One Function for Every ELEMENTS-Shaped Origin

No branching on which specific origin triggered this call — `IsInstance`
already handles `list`, `set`, `frozenset`, or any ABC (`Iterable`,
`Sequence`, `Collection`) identically via `isinstance(value, origin)`.
The origin table maps every one of these keys to this same function; the
"which ABC" distinction only matters for building the correct
`IsInstance` argument, which the dispatcher already provides via
`get_origin(annotation)`.

---

## 2. `container_type` Override — Why It Exists

Homogeneous `tuple[int, ...]` also fits the ELEMENTS shape exactly (a
tuple of unbounded length, every element the same type) — but the
dispatcher inspects `get_args()` on `tuple` *before* reaching the origin
table (see IsTyping's design notes on why tuple can't be a table entry),
and by that point it already knows the concrete container is `tuple`. The
`container_type` parameter lets the dispatcher pass that down explicitly,
rather than this function re-deriving it from `get_origin(annotation)` —
which would still correctly return `tuple` here, but re-deriving
something the caller already computed is unnecessary indirection.

---

## 3. Bare Generic (No Type Argument) Falls Back to a Pure Container Check

`get_args(list)` (no subscript) returns `()`. In that case, step 4 is
skipped entirely and `build_elements_rule` returns just
`IsInstance(list)` — equivalent to writing `list[Any]`, which is exactly
the right behavior: no item type was specified, so nothing about item
content should be constrained.

---

## 4. Recursive `build_typing_rule` Import Is Deferred, Not Circular by Accident

`_dispatch.py` imports every builder (via the origin table) at module
load time; if this file imported `build_typing_rule` from `_dispatch` at its own
top level, that would be a genuine circular import. Importing it inside
the function body breaks the cycle at import time while still resolving
correctly the first time this function actually runs.
"""