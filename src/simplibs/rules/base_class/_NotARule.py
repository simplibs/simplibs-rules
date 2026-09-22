from typing import Any, Protocol


class _NotARule(Protocol):
    """Structural stand-in for `Action` and future non-rule callable classes.

    Matches any callable carrying the `__not_rule__` marker attribute without
    requiring `Rule` to import or know about `Action` directly.
    """

    __not_rule__: Any

    def __call__(self, __data: Any) -> Any: ...


_DESIGN_NOTES = """
# _NotARule — Structural Protocol for Rule Exclusion

## Purpose
`_NotARule` is a private typing protocol used inside `Rule.py` to type-check
binary operators (`|`, `&`) when interacting with non-rule composable callables
such as `simplibs-actions`' `Action`.

## Why a Protocol?
1. **Layering Independence:** `simplibs-rules` is a lower-level library.
   Importing higher-level entities (like `Action`) here would introduce a circular
   or backward dependency.
2. **Type-Checker Accuracy:** By placing `_NotARule` as the first `@overload`
   variant in `Rule`'s operator signatures, static type checkers (MyPy, Pyright)
   will correctly infer that operator expressions involving `Action` hand control
   over to `Action`'s reflected operators (`__rand__`, `__ror__`) rather than
   treating `Action` as a plain predicate callable and wrapping it into `AllOf`/`AnyOf`.
"""