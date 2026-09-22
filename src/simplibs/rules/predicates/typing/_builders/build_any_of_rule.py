from typing import Any, get_args
# Outers
from ....base_class import Rule
from ....containers import AnyOf


def build_any_of_rule(annotation: Any) -> Rule:
    """ANY_OF process: value must satisfy at least one of the given member rules.

    Covers `Union[A, B, ...]`, `A | B` (types.UnionType), and therefore
    `Optional[T]` for free (`Optional[T]` is exactly `Union[T, None]` —
    no dedicated handling is needed; `NoneType` is a plain class, so it
    resolves through IsInstance(NoneType) like any other Union member).

    Args:
        annotation: The full Union annotation (e.g. `int | str | None`).

    Returns:
        An AnyOf combining one recursively-built Rule per union member.
    """

    # 1. Recursive build_typing_rule import — deferred, see elements_builder's notes
    from ..build_typing_rule import build_typing_rule

    # 2. Build one rule per member and combine
    members = get_args(annotation)
    return AnyOf(*(build_typing_rule(member) for member in members))


_DESIGN_NOTES = """
# any_of_builder — ANY_OF Process

## Purpose
The "value must match at least one alternative" process, covering both
spellings Python offers for the same concept: `typing.Union[A, B]` and
the `A | B` syntax (`types.UnionType`), which the origin table maps to
this same function under two different keys.

---

## 1. `Optional[T]` Needs No Special Case

`Optional[T]` is not a distinct typing construct — `get_origin` resolves
it identically to `Union[T, None]`, so `get_args` returns `(T, NoneType)`.
`NoneType` is an ordinary class (`type(None)`), so `build_typing_rule(NoneType)`
falls through to the plain `IsInstance(NoneType)` path in the dispatcher
just like any other member — `isinstance(None, NoneType)` is `True`, so
this correctly accepts `None`. No branch anywhere needs to know
`Optional` exists as a name.

---

## 2. `AnyOf` Already Flattens Nested Instances

If a Union itself contains a nested Union as a member (rare in practice,
since Python's typing machinery generally flattens `Union[Union[A, B], C]`
to `Union[A, B, C]` before this code ever sees it), `AnyOf`'s own
constructor already flattens same-type nested instances — see `AllOf`'s
design notes for the identical mechanism on the `&`/`AllOf` side. Nothing
extra is needed here to handle that case correctly.

---

## 3. Member Order Is Preserved, Not Sorted

`get_args()` returns union members in the order they were written in the
annotation, and `AnyOf(*members)` preserves that order. This matters for
diagnostics: `AnyOf.build_exception` (mirroring `AllOf`) reports against
the first-checked failing member, so `int | str` and `str | int` may
report a different "expected" member first on failure, even though both
accept the same values. This is a cosmetic diagnostic ordering
difference, not a correctness issue.
"""