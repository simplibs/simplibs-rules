from typing import Any
# Outers
from ....base_class import Rule
from ....predicates.introspection import IsCallable


def build_callable_rule(annotation: Any) -> Rule:
    """CALLABLE process: value must be callable.

    Covers Callable[[int, str], bool], Callable[..., ReturnType], and
    bare Callable — all reduce to the exact same runtime check.

    Args:
        annotation: The full Callable annotation. Its argument/return
            type information is intentionally not inspected — see the
            design notes below.

    Returns:
        IsCallable() — unconditionally, regardless of annotation detail.
    """

    # 1. Signature/arity/return-type checking is out of scope — see
    #    design notes. Every Callable[...] shape reduces to this.
    return IsCallable()


_DESIGN_NOTES = """
# callable_builder — CALLABLE Process

## Purpose
The one process in this package that intentionally discards its type
arguments entirely. `Callable[[int, str], bool]`, `Callable[..., Any]`,
and bare `Callable` all produce the exact same rule: `IsCallable()`.

---

## 1. Why Argument/Return-Type Checking Is Out of Scope

Validating that a callable's *signature* matches `[int, str] -> bool` at
runtime would require inspecting `inspect.signature(value)` and
attempting to reconcile parameter types, defaults, `*args`/`**kwargs`,
and return-type annotations (which are themselves optional and often
absent on the callable being validated) against the Callable annotation's
own argument list. This is a fundamentally different, much harder problem
than every other builder in this package solves — those all validate a
concrete *value* against a concrete *shape*; this would validate a
*function's declared contract* against another declared contract, which
static type checkers already do at type-check time and this library is
not attempting to reimplement at runtime.

`simplibs-validate` validates that a value **is callable** — the one
thing that can actually be checked cheaply and unambiguously at runtime —
and leaves argument/return-type conformance to the type checker or to the
caller's own explicit runtime checks if truly needed.

---

## 2. No Recursive `build_typing_rule` Calls

Since the argument/return type details are never inspected, `get_args()`
is not even called here — there is nothing in the annotation this builder
needs to look at beyond the fact that it dispatched here at all.
"""