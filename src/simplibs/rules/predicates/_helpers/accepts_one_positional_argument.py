import inspect
from typing import Any, Callable


def accepts_one_positional_argument(rule: Callable[[Any], bool]) -> bool:
    """Best-effort check that `rule` can be called as `rule(value)` — one
    positional argument, with nothing else mandatory.

    Args:
        rule: The callable to inspect.

    Returns:
        True if `rule` can be called with exactly one positional argument
        and no other parameter is mandatory (every additional positional
        parameter has a default, and every keyword-only parameter has a
        default; *args always qualifies). False if it requires zero or
        more than one mandatory positional argument, or any mandatory
        keyword-only argument. Defaults to True for uninspectable
        callables (e.g. some C-implemented builtins) — see design notes,
        section 3.
    """

    # 1. Signature retrieval
    try:
        signature = inspect.signature(rule)
    except (TypeError, ValueError):
        return True

    # 2. Check for mandatory keyword-only parameters
    keyword_only_params = [
        p for p in signature.parameters.values()
        if p.kind is inspect.Parameter.KEYWORD_ONLY
    ]
    if any(p.default is inspect.Parameter.empty for p in keyword_only_params):
        return False

    # 3. Check for variable positional arguments (*args)
    if any(p.kind is inspect.Parameter.VAR_POSITIONAL for p in signature.parameters.values()):
        return True

    # 4. Check for the existence of positional parameters
    positional_params = [
        p for p in signature.parameters.values()
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    if not positional_params:
        return False

    # 5. Check that extra positional parameters have default values
    for extra_param in positional_params[1:]:
        if extra_param.default is inspect.Parameter.empty:
            return False

    # 6. Return success
    return True


_DESIGN_NOTES = """
# accepts_one_positional_argument — UserRule's Arity Guard

## Purpose
Catches, at UserRule construction time, any callable that structurally
cannot be called as `rule(value)` — a single positional argument, with
nothing else mandatory. Extracted as its own function so it can be
tested directly against arbitrary callables without constructing a
UserRule to exercise it.

---

## 1. Why This Exists: What It Prevents

Without this check, a callable requiring more than `rule(value)` can
supply (e.g. `lambda x, y: x > y`, or a required keyword-only argument)
would be accepted by UserRule's constructor, only to raise a TypeError
the first time `is_valid(value)` actually calls it. Because
`UserRule.is_valid` catches and swallows every exception from the
wrapped callable (see UserRule's own design notes, section 1), that
TypeError would silently become "validation failed" — a misleading
diagnosis of the value, when the real problem is that the rule itself
was never callable the way UserRule needs it to be. This check turns
that into an immediate, clear ParamError at the point the broken rule is
defined, instead of a confusing false negative buried in later
validation results.

---

## 2. Keyword-Only Parameters Are Checked First, Unconditionally

A callable can have `*args` (which always accepts a single positional
value) and *still* be uncallable as `rule(value)`, if it also declares a
mandatory keyword-only parameter — e.g. `lambda *args, key: True`. An
earlier draft checked `*args` first and returned early on finding it,
which meant a mandatory keyword-only parameter after `*args` was never
inspected at all. The keyword-only check now runs first and
unconditionally, before any early return, so no later branch can skip
past it.

---

## 3. Otherwise Permissive, Not Exhaustive

Beyond the keyword-only check above, this function is still
deliberately permissive where ambiguity doesn't lead to a guaranteed
runtime failure:
* A callable requiring two or more *positional* arguments (no default on
  the second) is rejected — see step 4 — but a callable accepting extra
  *optional* positional or keyword-only parameters is accepted, since
  `rule(value)` would supply enough to satisfy it.
* Uninspectable callables (`inspect.signature()` raising TypeError/
  ValueError — some C-implemented builtins) are accepted by default:
  treating "can't tell" as "reject" would produce false-positive
  rejections of perfectly valid callables this function simply cannot
  introspect, which is a worse failure mode than occasionally letting an
  actually-broken C callable through to fail at call time instead of at
  construction time.

---

## 4. Called Once, at UserRule Construction — Not Per Validation

Like every other one-time setup cost in this library (rule compilation
in validate_call, decomposition in IsTyping), this check runs exactly
once, when `UserRule(rule)` is constructed — never inside `is_valid()`.
The cost of `inspect.signature()` and a short walk over its parameters is
negligible against that one-time construction, and irrelevant to the
per-call validation hot path.
"""