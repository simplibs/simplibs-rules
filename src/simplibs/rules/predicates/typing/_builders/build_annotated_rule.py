from typing import Any, get_args
# Outers
from ....base_class import Rule
from ....containers import AllOf, Compose


def build_annotated_rule(annotation: Any) -> Rule:
    """ANNOTATED process: combine the underlying type with any Rule metadata.

    Covers Annotated[X, ...metadata...]. The underlying annotation X is
    always decomposed via build_typing_rule(). Any metadata item that is itself
    a Rule instance (or a plain callable predicate) is combined with it
    via AllOf — this is how simplibs-validate rules attach themselves to
    ordinary typing annotations, e.g.:

        Annotated[int, greater_than(0)]
        Annotated[str, is_string & has_length(min_length=1)]

    Metadata items that are neither a Rule nor callable (plain strings,
    framework-specific objects like a Pydantic Field(), ...) are ignored
    — they carry no validation meaning for this library.

    Args:
        annotation: The full Annotated construct.

    Returns:
        build_typing_rule(X) alone if no metadata item is a Rule/callable,
        otherwise an AllOf combining it with every such metadata item.
    """

    # 1. Recursive build_typing_rule import — deferred, see elements_builder's notes
    from ..build_typing_rule import build_typing_rule

    # 2. get_args(Annotated[X, *meta]) == (X, *meta) — the real
    #    annotation is always the first element; the rest is metadata
    underlying, *metadata = get_args(annotation)

    # 3. Base rule from the underlying (unwrapped) annotation
    parts: list[Rule] = [build_typing_rule(underlying)]

    # 4. Extract any metadata items that are validation predicates:
    #    a Rule instance, or a plain callable (lambda / function)
    for item in metadata:
        if isinstance(item, Rule):
            parts.append(item)
        elif callable(item):
            parts.append(Compose(lambda value: value, item))

    # 5. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# annotated_builder — ANNOTATED Process

## Purpose
`Annotated[X, ...]` attaches arbitrary metadata to an annotation — see
PEP 593. This library specifically recognizes metadata items that are a
`Rule` instance (or a plain callable predicate) and folds them into the
composed rule for X, which is precisely the mechanism PEP 593 was
designed to enable for frameworks like this one.

---

## 1. How simplibs-validate Rules Attach to typing Annotations

Rather than inventing a separate parallel syntax, `Annotated` is the
sanctioned extension point: `Annotated[int, greater_than(0)]` or `rule.annotated(int)`
reads as ordinary `int` to a type checker (mypy sees strictly `int`), while
IsTyping decomposes it into `AllOf(IsInstance(int), GreaterThan(0))` at
runtime. No new typing-adjacent syntax was needed — this reuses stdlib
machinery exactly as intended.

---

## 2. Plain Callables Are Accepted Too, Not Just `Rule` Instances

Consistent with `validate()`/`Rule.validate()` already accepting a plain
callable (lambda, function) as a predicate alongside `Rule` instances.
A metadata item that is callable but not a `Rule` is wrapped
via `Compose(identity, predicate)` rather than requiring the user to
formally subclass `Rule` just to attach `Annotated[int, lambda v: v > 0]`.

---

## 3. Non-Predicate Metadata Is Silently Ignored, Not Rejected

`Annotated[int, "some docstring", SomeOtherFrameworksField(...)]` is
valid and common — other tools attach their own metadata to the same
annotation, and this library has no business rejecting or erroring on
metadata it doesn't understand. Only items that are a `Rule` or callable
are treated as validation predicates; everything else passes through
untouched, exactly as PEP 593 intends.

---

## 4. Multiple Rule/Callable Metadata Items Compose via AllOf

`Annotated[int, greater_than(0), divisible_by(2)]` combines both — no
conflict handling needed, since combining independent predicates with
AND is always well-defined.
"""