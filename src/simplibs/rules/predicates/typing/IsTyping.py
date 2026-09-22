from typing import Any
# Outers
from ...base_class import Rule
# Inners
from .build_typing_rule import build_typing_rule


class IsTyping(Rule):
    """Value must satisfy the given typing annotation.

    Rule:
        Recursively decomposed via get_origin()/get_args() into a
        composed Rule tree (IsInstance, AllOf, AnyOf, ForEach, ...) built
        once at construction time.

    Example:
        validate(value, IsTyping(list[int]))
        validate(value, IsTyping(dict[str, int] | None))
        validate(value, IsTyping(Literal["draft", "published"]))
    """

    __slots__ = ("annotation", "rule")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, annotation: Any) -> None:

        # 1. Store the original annotation for diagnostics/introspection
        self.annotation = annotation

        # 2. Decompose it once, up front — not on every is_valid() call
        self.rule = build_typing_rule(annotation)

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Delegate entirely to the pre-built composed rule
        return self.rule.is_valid(value)

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Delegate to the composed rule's own diagnostic — it already
        #    knows exactly which sub-check failed (mirrors AllOf/AnyOf
        #    delegating to their own first-failing child)
        return self.rule.build_exception(value, value_name=value_name, context=context)


_DESIGN_NOTES = """
# IsTyping — Annotation-Driven Validation Rule

## Purpose
The public entry point of this whole sub-package: wraps an arbitrary
typing annotation and validates values against it, by building — once,
at construction time — the equivalent composed Rule tree via
`_dispatch.build_typing_rule()`.

---

## 1. Decomposition Happens in `__init__`, Not `is_valid`

`build_typing_rule(annotation)` recursively walks the entire annotation and
constructs every nested `IsInstance`/`AllOf`/`AnyOf`/`ForEach` up front,
exactly once, when `IsTyping(annotation)` is constructed. `is_valid()`
and `build_exception()` are then pure delegation to that already-built
`self.rule` — repeated validation against the same `IsTyping` instance
(e.g. reused inside a loop, or as a composed_rule building block) never
re-walks the annotation.

---

## 2. `annotation` Is Stored, Even Though `self.rule` Does the Real Work

Kept for introspection/debugging (e.g. `repr(is_typing_instance)` or
future tooling that wants to know what annotation a given `IsTyping`
instance was built from) — `self.rule` alone would not let a caller
recover the original annotation once decomposed.

---

## 3. `build_exception` Delegates Rather Than Re-Deriving

Mirrors `AllOf`/`AnyOf`'s own pattern of delegating to the child rule
that actually failed, rather than constructing a generic "value doesn't
match this annotation" message from scratch. Since `self.rule` is
already the exact composed tree describing the annotation, its own
`build_exception` already produces the most specific diagnostic
available — re-deriving one here would either duplicate that logic or
produce a strictly worse, less specific message.
"""