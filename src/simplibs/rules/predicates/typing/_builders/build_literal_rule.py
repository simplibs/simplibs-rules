from typing import Any, get_args

# Outers
from ....base_class import Rule
from ....predicates.logic import IsIn


def build_literal_rule(annotation: Any) -> Rule:
    """LITERAL process: value must equal one of the given literal values.

    Covers Literal[1, 2, 3], Literal["a", "b"], Literal[True, False], and
    mixed literal sets.

    Args:
        annotation: The full Literal annotation (e.g. `Literal["a", "b"]`).

    Returns:
        An IsIn rule over the literal's exact allowed values with strict type checking.
    """

    # 1. Extract the literal values directly — no recursion needed,
    #    Literal's arguments are values, not nested annotations
    allowed_values = get_args(annotation)

    # 2. Delegate straight to IsIn with strict=True to enforce exact type matching
    return IsIn(allowed_values, strict=True)


_DESIGN_NOTES = """
# literal_builder — LITERAL Process

## Purpose
The only ELEMENTS-adjacent process whose type arguments are concrete
values rather than nested annotations. `Literal[1, 2, "x"]` means
"exactly one of these values", which `IsIn(..., strict=True)` expresses
precisely without needing a custom layer-1 rule.

---

## 1. No Recursive `build_typing_rule` Call

Every other builder in this package recursively decomposes its type
arguments via `build_typing_rule()`, because those arguments are themselves
annotations (`list[int]`'s `int`, `dict[str, int]`'s `str`/`int`, ...).
`Literal`'s arguments are different in kind — they are the literal
*values* themselves (`1`, `"x"`, `True`), not types describing what kind
of value is acceptable. Passing them to `build_typing_rule()` would be a type
error (`build_typing_rule(1)` has no meaningful interpretation). `IsIn` compares
by value directly, which is exactly what `Literal` means.

---

## 2. Strict Type Matching (`strict=True`)

By default, Python evaluates `True == 1` and `False == 0`. To remain fully
faithful to type checker semantics (where `Literal[1]` and `Literal[True]`
are distinct types), `build_literal_rule` passes `strict=True` to `IsIn`.
This ensures that `Literal[1]` rejects `True` and `Literal[True]` rejects `1`
by validating both value equality and exact type matching (`type(value) is type(option)`).
"""