from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsAny(Rule):
    """Value always passes, regardless of type or content.

    Rule:
        True

    Example:
        validate(value, IsAny())

    Note:
        Not intended for direct use in ordinary validation expressions —
        `IsAny` exists as the structural counterpart to `typing.Any` for
        `IsTyping`'s recursive annotation decomposition, where an
        annotation slot that accepts anything still needs a concrete Rule
        to plug into the composed AllOf/AnyOf tree.
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Always passes — mirrors typing.Any's "no constraint" semantics
        return True

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Unreachable in practice — is_valid never returns False,
        #    so this only exists to satisfy Rule's abstract contract
        return ValidationError(
            error_name="IS_ANY_UNREACHABLE_ERROR",
            label=value_name,
            expected="any value",
            value=value,
            problem="IsAny.is_valid() unexpectedly returned False.",
            context=context,
            how_to_fix=("Check validation logic state.",),
            exception=RuntimeError,
        )


# ----------------------------------------------------------------------
# Module-level internal singleton for IsTyping recursive decomposition
# ----------------------------------------------------------------------
_IS_ANY = IsAny()


_DESIGN_NOTES = """
# IsAny — Unconstrained "Accepts Everything" Rule

## Purpose
Structural counterpart to `typing.Any`, for use by `IsTyping`'s recursive
annotation decomposition. When an annotation contains `Any` somewhere
(e.g. `dict[str, Any]`, `list[Any]`), that slot still needs a concrete
`Rule` instance to plug into the composed tree — `IsAny` is that rule,
and it imposes no constraint whatsoever.

---

## 1. `return True`, Not `isinstance(value, object)`

Every value in Python is an instance of `object`, so
`isinstance(value, object)` and a hardcoded `True` are behaviorally
identical — the isinstance check can never return False. Writing it out
anyway would misleadingly suggest a real check is happening. `return
True` is kept as the honest, direct statement of what `Any` actually
means: no constraint at all, not "a constraint that happens to always
pass".

---

## 2. `build_exception` Is Unreachable By Construction

Since `is_valid` never returns `False`, `build_exception` can never be
invoked through the normal `Rule.validate()` / `AllOf`/`AnyOf` execution
paths. It exists only because `Rule` is abstract and requires it — same
rationale as `AllOf`'s own `ALL_OF_UNREACHABLE_ERROR` fallback branch.

---

## 3. Not a General-Purpose Shortcut

`IsAny` is not exposed for the same kind of everyday composition as
`is_string`/`is_integer`/etc. — `validate(value, IsAny())` is a no-op a
caller would never intentionally write by hand. It exists specifically
so `IsTyping`'s annotation walker always has *something* concrete to
append to `parts` when it encounters `Any`, keeping that walker's own
logic uniform (every annotation slot produces exactly one Rule) rather
than needing a special "skip this slot" branch.

---

## 4. Internal Singleton Naming Convention (`_IS_ANY`)

The module instantiates a single `_IS_ANY` singleton. The leading underscore
explicitly signals that it is private to internal typing helpers and should
not be imported or re-exported as a public API object.
"""