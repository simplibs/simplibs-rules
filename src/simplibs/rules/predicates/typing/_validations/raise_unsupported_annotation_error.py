from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_unsupported_annotation_error(annotation: Any) -> NoReturn:
    """Raise a ParamError for a typing annotation IsTyping cannot decompose.

    Args:
        annotation: The unrecognized annotation (or annotation fragment,
            for nested/recursive failures) that triggered this error.

    Raises:
        ParamError: Always.
    """
    raise ParamError(
        error_name="UNSUPPORTED_TYPING_ANNOTATION_ERROR",
        label="annotation",
        expected="A supported type or typing annotation",
        value=annotation,
        problem=f"Annotation {annotation!r} is not a recognized type or typing construct.",
        how_to_fix=(
            "Use a plain class (e.g. int, str, CustomClass).",
            "Use standard generics (list[T], set[T], dict[K, V], tuple[...]).",
            "Use special typing constructs (Union / |, Optional, Literal, Annotated).",
            "Use Callable, Type, NewType, or Any.",
            "If using ForwardRef or complex type aliases, resolve them to concrete types first.",
        ),
    )


_DESIGN_NOTES = """
# raise_unsupported_annotation_error — IsTyping Diagnostic Helper

## Purpose
Single point of failure for every "I don't know how to build a Rule for
this annotation" case across the dispatcher and every builder — mirrors
the `raise_param_*_error` helpers already used by layer-1 rules
(`raise_has_length_param_conflict_error`, `raise_param_not_container_error`,
...), applied here to typing decomposition instead of constructor
parameters.

---

## 1. Reused at Every Recursion Depth

Builders call `build_typing_rule()` recursively on nested annotation slots (a
list's item type, a dict's value type, a Union member, ...). If any of
those nested calls hits an unsupported construct, this same helper is
raised from that inner frame — so the reported `annotation` is always the
specific fragment that failed, not just the top-level annotation the
caller originally passed to `IsTyping(...)`. This makes diagnosing
`IsTyping(dict[str, SomeUnsupportedThing])` point directly at
`SomeUnsupportedThing`, not at the whole dict annotation.

---

## 2. Multi-Line Tuple Formatting for How-to-Fix

To eliminate hard-to-read line-wrapped strings in error cards, `expected` is
a clean string summary, while `how_to_fix` uses a tuple of strings. The
exception subsystem renders these items on distinct, structured lines, giving
users a clear, categorized list of supported typing constructs and remedy steps.
"""