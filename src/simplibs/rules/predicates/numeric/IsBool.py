from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsBool(Rule):
    """Value must be a boolean (True or False).

    Rule:
        isinstance(value, bool)

    Example:
        validate(value, IsBool())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is strictly a bool
        return isinstance(value, bool)

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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not a boolean."
        how_to_fix = "Provide a boolean value (True or False)."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_BOOL_ERROR",
            label=value_name,
            expected="a boolean (True or False)",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsBool — Boolean Type Validation Rule

## Purpose
The `IsBool` rule validates that an input value is strictly a `bool`
instance — either `True` or `False`.

---

## 1. Execution Rationale & Safeguards

* **Strict Type Check:**
  Uses `isinstance(value, bool)`. Since Python's `bool` is a subclass of
  `int`, this is a legitimately narrower check than `isinstance(value,
  int)` — every `bool` is an `int`, but not every `int` is a `bool`.

---

## 2. Relationship to the Rest of `predicates/numeric/`

* **The One Rule That *Wants* `bool`:**
  Every other rule in this sub-package explicitly *excludes* `bool`
  (`isinstance(value, int) and not isinstance(value, bool)` in
  `IsInteger`, `IsNumber`, `IsPrimitiveNumber`, ...), treating `True`/
  `False` as their own distinct type rather than as the integers `1`/`0`.
  `IsBool` is the mirror image of that convention: it is the rule that
  specifically wants *only* what all the others reject.
* **No Internal Reuse Helper:**
  Unlike `IsInteger`/`IsNumber`/`IsPrimitiveNumber`/`IsContainer`, this
  module does not expose a module-level `is_bool = IsBool().is_valid`
  helper, since — at the time of writing — no other rule's constructor
  needs a fast internal bool-type guard. Add one if that changes,
  following the existing pattern.

---

## 3. Exception Card Design

* **Error Classification:** Uses `IS_BOOL_ERROR` wrapping a `TypeError`.
* **Fix Guidance:** Advises providing the literal `True`/`False` boolean
  value.
"""