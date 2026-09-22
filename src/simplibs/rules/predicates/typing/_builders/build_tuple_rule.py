from typing import Any, get_args
# Outers
from ....base_class import Rule
from ....containers import AllOf
from ....predicates.introspection import HasLength, IsInstance
# Inners
from .build_elements_rule import build_elements_rule


def build_tuple_rule(annotation: Any) -> Rule:
    """TUPLE process: handle both homogeneous and positional tuple annotations.

    Inspects `get_args(annotation)` to route between:
    1. Homogeneous / unbounded tuples (`tuple`, `tuple[T, ...]`) -> elements rule
    2. Fixed-length heterogeneous tuples (`tuple[A, B, C]`) -> positional rule

    Args:
        annotation: A tuple typing construct (e.g., `tuple`, `tuple[int, ...]`,
            or `tuple[str, int, bool]`).

    Returns:
        A composed Rule validating the specific tuple structure.
    """

    # 1. Getting arguments
    args = get_args(annotation)

    # 2. Unsubscripted `tuple` or homogeneous `tuple[T, ...]`
    if not args or _is_homogeneous_tuple_args(args):
        return build_elements_rule(annotation, container_type=tuple)

    # 3. Fixed-length heterogeneous `tuple[A, B, C]`
    return _build_positional_rule(annotation, args)


def _is_homogeneous_tuple_args(args: tuple[Any, ...]) -> bool:
    """True if `args` matches the (T, Ellipsis) shape of `tuple[T, ...]`.

    Used to distinguish homogeneous, unbounded-length tuples from
    fixed-length, per-index positional tuples.
    """
    return len(args) == 2 and args[1] is Ellipsis


def _build_positional_rule(annotation: Any, args: tuple[Any, ...]) -> Rule:
    """Build a positional rule for fixed-length heterogeneous tuples.

    Combines an IsInstance(tuple) check, an exact length check, and one
    independent validation rule per tuple index.
    """
    # Recursive build_typing_rule import — deferred to avoid circular imports
    from ..build_typing_rule import build_typing_rule

    # 1. Base type and exact arity checks
    parts: list[Rule] = [
        IsInstance(tuple),
        HasLength(length=len(args)),
    ]

    # 2. One independent rule per position
    for index, item_annotation in enumerate(args):
        item_rule = build_typing_rule(item_annotation)
        parts.append(_at_index(index, item_rule))

    # 3. Collapse into AllOf rule
    return AllOf(*parts)


def _at_index(index: int, rule: Rule):
    """Build a closure checking if `rule` holds at a specific tuple position."""
    def check(value) -> bool:
        return rule.is_valid(value[index])
    return check


_DESIGN_NOTES = """
# tuple_builder — Homogeneous & Positional Tuple Processing

## Purpose
Handles all `tuple` origin validations. Because Python tuples can represent
both unbounded homogeneous containers (`tuple[int, ...]`) and fixed-length
heterogeneous structures (`tuple[str, int]`), this builder inspects `get_args()`
to delegate between the shared `build_elements_rule` and dedicated local
positional logic.

---

## 1. Homogeneous vs. Positional Routing

- Unsubscripted `tuple` (args == ()) is equivalent to `tuple[Any, ...]`.
- `tuple[T, ...]` uses Ellipsis as the second argument.
Both shapes delegate to `build_elements_rule(annotation, container_type=tuple)`.
All other subscripted tuple shapes represent fixed-length structures and
are processed positionally.

---

## 2. Per-Position Rules via Closure Predicates

Each position check (`value[index]` satisfies `rule`) uses a lightweight local
closure (`_at_index`). A dedicated `Rule` subclass is omitted to avoid unnecessary
overhead since these checks exist solely within this builder's composed `AllOf`.

---

## 3. Explicit Arity Validation (`HasLength`)

Position checks assume the tuple has sufficient elements. Including
`HasLength(length=len(args))` guarantees that arity mismatches fail gracefully
with a validation error rather than raising an unhandled `IndexError`.
"""