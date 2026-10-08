import types
from typing import Annotated, Any, Literal, Union, get_args, get_origin
# Outers
from ....base_class import Rule


def format_annotation(annotation: Any) -> str:
    """Return a compact, readable spelling of a typing annotation.

    Used to describe a composed rule tree by the annotation it was built
    from ("list[int]") instead of by its internal structure
    ("list & each int").

    Args:
        annotation: Any annotation or annotation fragment build_typing_rule
            accepts — a plain class, a Rule instance, a NewType, or a typing
            construct.

    Returns:
        A short text such as "int", "list[int]", "int | None",
        "Literal['a', 'b']" or "dict[str, int]". Anything unrecognized
        falls back to repr(), so supported annotations never raise.
    """

    # 1. Constants and special forms
    if annotation is Any:
        return "Any"
    if annotation is None or annotation is type(None):
        return "None"
    if annotation is Ellipsis:
        return "..."

    # 2. Callable's argument list — Callable[[int, str], bool]
    if isinstance(annotation, list):
        return "[" + ", ".join(format_annotation(item) for item in annotation) + "]"

    # 3. Constructs without an origin — classes, Rule instances, NewType, ...
    origin = get_origin(annotation)
    if origin is None:
        return _format_plain(annotation)

    # 4. Union — Union[A, B], Optional[A], A | B
    if origin in (Union, types.UnionType):
        return " | ".join(format_annotation(member) for member in get_args(annotation))

    # 5. Literal — values, not nested annotations
    if origin is Literal:
        return "Literal[" + ", ".join(repr(value) for value in get_args(annotation)) + "]"

    # 6. Annotated
    if origin is Annotated:
        return _format_annotated(annotation)

    # 7. Any other generic — list[int], dict[str, int], Callable[[int], str], ...
    name = getattr(origin, "__name__", None) or repr(origin)
    args = get_args(annotation)
    if not args:
        return name
    return f"{name}[{', '.join(format_annotation(arg) for arg in args)}]"


def _format_plain(annotation: Any) -> str:
    """Format an annotation that has no typing origin."""

    # 1. Rule instance used directly as an annotation
    if isinstance(annotation, Rule):
        return annotation.describe()

    # 2. Plain class
    if isinstance(annotation, type):
        return annotation.__name__

    # 3. NewType and other named objects
    name = getattr(annotation, "__name__", None)
    if isinstance(name, str) and name:
        return name

    # 4. Anything else
    return repr(annotation)


def _format_annotated(annotation: Any) -> str:
    """Format Annotated[X, ...] — X plus only the metadata that acts as a rule."""

    # 1. get_args(Annotated[X, *meta]) == (X, *meta)
    underlying, *metadata = get_args(annotation)

    # 2. Keep only metadata build_annotated_rule also treats as validation
    #    (a Rule or a callable) — everything else is ignored there too
    parts = [
        _describe_metadata(item)
        for item in metadata
        if isinstance(item, Rule) or callable(item)
    ]

    # 3. Without validating metadata, Annotated[X, ...] reads as plain X
    base = format_annotation(underlying)
    if not parts:
        return base
    return f"Annotated[{base}, {', '.join(parts)}]"


def _describe_metadata(item: Any) -> str:
    """Describe one Annotated metadata item."""
    if isinstance(item, Rule):
        return item.describe()
    return getattr(item, "__name__", repr(item))


_DESIGN_NOTES = """
# format_annotation — Readable Annotation Spelling

## Purpose
Turns a typing annotation into the short text a developer would write
("list[int]", "int | None", "dict[str, int]"). `build_typing_rule` attaches
this text to every composed rule it builds (via `Described`), so error
messages can name the annotation instead of its decomposed internals.

---

## 1. Why Not Just `repr(annotation)`

`repr()` gives "<class 'int'>" for a plain class, a "typing." prefix for
many constructs, and module-qualified names ("__main__.User") inside
generics. Recursing by hand keeps every level in the same short style and
lets `Callable[[int], str]`'s argument list and `Literal`'s raw values
format correctly.

---

## 2. Mirrors build_annotated_rule's Metadata Filter

Annotated metadata appears in the text only if `build_annotated_rule`
would also treat it as validation (a Rule or a callable). Other metadata
(strings, framework objects) is invisible to both, so the text never
mentions something that does not take part in validation.

---

## 3. Falls Back Instead of Failing

Anything unrecognized falls back to `repr()`. This runs while a rule tree is
built, and an exotic annotation must not break construction just because
its text could not be prettified. (A user `Rule` used as an annotation is
described through its own `describe()`, which is contractually non-raising.)
"""
