import types
from typing import Any, Union, get_args, get_origin
# Outers
from ....base_class import Rule
from ....containers import AllOf, AnyOf
from ....predicates.introspection import IsSubclass, IsType
from .._validations import raise_unsupported_annotation_error


def build_type_rule(annotation: Any) -> Rule:
    """TYPE process: value must be a class object, optionally a subclass of T.

    Covers `Type[T]` / `type[T]` (including `T` being itself a Union, in
    which case any one of the union's members is an acceptable base),
    `type[Any]` (unconstrained class object), and bare `Type`/`type` (no argument).

    Args:
        annotation: The full annotation (e.g. `type[MyBase]`,
            `type[MyBase | OtherBase]`, or `type[Any]`).

    Returns:
        IsType() alone if no argument or `Any` is given, otherwise an AllOf adding
        a subclass constraint (IsSubclass directly, or AnyOf of several
        IsSubclass checks for a Union base).
    """

    # 1. Definice základního pravidla
    parts: list[Rule] = [IsType()]

    # 2. Zpracování argumentů
    args = get_args(annotation)
    if args:
        base = args[0]
        base_origin = get_origin(base)

        # 2.1 Any base — type[Any] — behaves like bare type (unconstrained class)
        if base is Any:
            pass

        # 2.2 Union base — type[A | B] — any one base is acceptable
        elif base_origin in (Union, types.UnionType):
            members = get_args(base)
            if not all(isinstance(member, type) for member in members):
                raise_unsupported_annotation_error(annotation)
            subclass_checks = [IsSubclass(member) for member in members]
            parts.append(AnyOf(*subclass_checks))

        # 2.3 Plain class base — type[MyBase]
        elif isinstance(base, type):
            parts.append(IsSubclass(base))

        # 2.4 Anything else (e.g. type[SomeGeneric[int]]) —
        #    not supported; see design notes, section 2
        else:
            raise_unsupported_annotation_error(annotation)

    # 3. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# type_builder — TYPE Process

## Purpose
`Type[T]` asks whether the value **is itself a class**, optionally one
inheriting from `T` — a statement about the value being a type object,
not about instances of anything. This distinguishes it from every other
builder in this package, which validate instances against a shape.

---

## 1. Union Base Support (`Type[A | B]`)

`type[A | B]`'s single type argument is itself a Union, not a plain
class — `get_origin(base)` detects this the same way `_dispatch.py`
detects a top-level Union, and each member becomes its own
`IsSubclass(member)`, combined with `AnyOf`. This reuses the *detection*
logic conceptually shared with `any_of_builder`, but not the function
itself — `any_of_builder.build_any_of_rule` recursively calls
`build_typing_rule()` on each member (since Union members are usually meant to
be validated as instances), which is wrong here: `Type[A | B]`'s members
must become `IsSubclass` checks, not `IsInstance` checks. Duplicating the
small amount of union-unpacking logic locally was judged clearer than
trying to parametrize `any_of_builder` to serve two different meanings
of "what does a Union member turn into".

---

## 2. Support for `type[Any]` and Unsupported Non-Class Bases

`type[Any]` is supported and explicitly means "any class object at all",
behaving identically to bare `type` / `Type` by returning just `IsType()`.
Because `Any` is a special construct rather than a standard `type` instance,
it is handled as an explicit fast path (`base is Any`) before non-class base
checks.

Conversely, complex parameterizations like `type[SomeGeneric[int]]` or other
non-class, non-Union type arguments remain unsupported and raise
`raise_unsupported_annotation_error`.

---

## 3. Redundancy With `IsSubclass` Itself

Same rationale as the composed-layer `type_rule`'s own design notes:
`IsSubclass.is_valid` already checks `isinstance(value, type)` internally,
so the leading `IsType()` is technically redundant once a base is given —
kept for a consistent base predicate and a clearer first-failure
diagnostic.
"""