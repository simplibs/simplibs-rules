from collections.abc import Iterable, Iterator
from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsReiterable(Rule):
    """Value must be iterable and safe to iterate more than once (not a one-shot iterator).

    Rule:
        isinstance(value, Iterable) and not isinstance(value, Iterator)

    Example:
        validate(value, IsReiterable())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Iterable, but not an iterator (generators, file objects, map/zip/filter, ...)
        return (
            isinstance(value, Iterable)
            and not isinstance(value, Iterator)
        )

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed phrase — the rule has no parameters
        return "re-iterable"

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Prepare data
        # 1.1 When value is not iterable at all
        if not isinstance(value, Iterable):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not iterable."
            how_to_fix = "Provide a re-iterable container (e.g., list, tuple, set)."

        # 1.2 When value is a one-shot iterator
        else:
            problem = (
                f"Value of type '{type(value).__name__}' is a one-shot iterator: "
                "checking its items would consume it, so the receiving code would get it exhausted."
            )
            how_to_fix = (
                "Pass a list, tuple or set (e.g. list(value)) instead of the iterator, "
                "or annotate the parameter as plain Iterable (without an item type)."
            )

        # 2. Build the exception
        return ValidationError(
            error_name="IS_REITERABLE_ERROR",
            label=value_name,
            expected="re-iterable value (e.g. list, tuple, set), not a one-shot iterator",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=TypeError,
        )


_DESIGN_NOTES = """
# IsReiterable — Re-Iterable Value Validation Rule

## Purpose
The `IsReiterable` rule validates that a value is iterable AND can be
iterated more than once — a list, tuple, set, dict, range, string, a dict
view — as opposed to a one-shot iterator (generator, file object,
`map`/`zip`/`filter`/`enumerate` result, a hand-written iterator class).

It exists for one reason: any rule that checks the *items* of a value
(`ForEach`, and through it `Iterable[T]`) has to walk it, and walking a
one-shot iterator consumes it. The value then reaches the validated code
exhausted, silently empty. `IsReiterable` is the cheap guard placed in
front of such a check.

---

## 1. Execution Rationale & Safeguards

* **ABC Checks, No Side Effects:**
  `isinstance(value, Iterable)` and `isinstance(value, Iterator)` are
  structural ABC checks (`__iter__` / `__iter__` + `__next__`). Unlike
  calling `iter(value)`, they never create or advance anything.
* **Iterator Means One-Shot:**
  By the iterator protocol an iterator returns itself from `__iter__`, so
  a second pass sees what the first one left behind. A class whose
  `__iter__` returns a *fresh* iterator each time is not an `Iterator`
  and is accepted.
* **Why `Iterable`, Not `hasattr(value, "__iter__")`:**
  `hasattr` is also true for a class object (`hasattr(list, "__iter__")`).
  The ABC check looks at the type of the value, matching `IsInstance(Iterable)`
  used by the typing layer. Objects iterable only through the legacy
  `__getitem__` protocol are not recognized as iterable.
* **Dual Diagnostic Path (`build_exception`):**
  Both failures are a `TypeError` (`IS_REITERABLE_ERROR`) with a different
  `problem`: "not iterable", or "one-shot iterator" with the fix
  (pass a list/tuple/set, or annotate plain `Iterable`).

---

## 2. What It Deliberately Does Not Do

* It never advances or inspects the value's items — that is the job of
  `ForEach`.
* It does not try to "peek" at an iterator to be helpful; whatever is passed
  in stays untouched.

---

## 3. Description

`describe()` returns "re-iterable" — what the value must be. A short
fragment that containers and the typing layer compose into larger texts;
the failure card keeps its own `expected` sentence.
"""
