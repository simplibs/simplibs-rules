from typing import Any, Callable
from simplibs.exception import ValidationError
# Outers
from ..base_class import Rule
# Inners
from ._helpers import as_predicate, build_child_exception
from ._init_validators import (
    raise_requires_at_least_one_rule_error,
    raise_rule_param_not_callable
)


class AllOf(Rule):
    """Value must satisfy every one of the given rules.

    Rule:
        all(rule(value) for rule in rules)

    Example:
        validate(value, AllOf(IsInteger(), GreaterThan(0)))
        validate(value, IsInteger() & GreaterThan(0))
    """

    __slots__ = ("rules",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *rules: Rule | Callable[[Any], bool]) -> None:

        # 1. Parameter validation
        if not rules:
            raise_requires_at_least_one_rule_error("AllOf")

        # 2. Flatten nested AllOf instances (e.g. from `a & b & c` chaining)
        #    into a single flat rule list, rather than nesting AllOf(AllOf(...), ...)
        flattened: list[Rule | Any] = []
        for rule in rules:
            if not callable(rule):
                raise_rule_param_not_callable("AnyOf", rule)
            if type(rule) is AllOf:
                flattened.extend(rule.rules)
            else:
                flattened.append(rule)

        # 3. Parameter assignment
        self.rules = tuple(flattened)

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value satisfies all rules
        return all(
            as_predicate(rule)(value)
            for rule in self.rules
        )

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Raise the exception for the first failing rule
        for rule in self.rules:
            if not as_predicate(rule)(value):
                return build_child_exception(rule, value, value_name, context)

        # 2. Fallback (build exception if all rules unexpectedly passed)
        return ValidationError(
            error_name="ALL_OF_UNREACHABLE_ERROR",
            label=value_name,
            expected="value satisfying all rules",
            value=value,
            problem="All rules unexpectedly passed during error construction.",
            context=context,
            how_to_fix=("Check validation logic state.",),
            exception=RuntimeError,
        )


_DESIGN_NOTES = """
# AllOf — Logical AND Container Validation Rule

## Purpose
The `AllOf` rule aggregates multiple validation rules or callables,
requiring an input value to satisfy ALL contained rules (logical
conjunction / AND). It is also the rule constructed under the hood by
`Rule.__and__`/`Rule.__rand__` (`rule1 & rule2`).

---

## 1. Execution Rationale & Short-Circuit Evaluation

* **Constructor Fail-Fast:**
  Requires at least one child rule during initialization via
  `raise_requires_at_least_one_rule_error` (`ParamError`).
* **Short-Circuit Evaluation:**
  Uses Python's native `all()` to short-circuit upon encountering the first
  failing rule.
* **Child Exception Delegation:**
  In `build_exception`, iterates through rules, finds the first failing
  rule, and delegates exception generation to `build_child_exception`.

---

## 2. Self-Flattening Constructor

* **Why It's Needed:**
  `Rule.__and__` builds `AllOf` instances one pair at a time, so a chained
  expression like `a & b & c` evaluates left-to-right as `(a & b) & c`,
  which — without flattening — would construct a nested
  `AllOf(AllOf(a, b), c)` rather than a flat `AllOf(a, b, c)`.
* **Why Nesting Would Be a Problem:**
  `build_exception` delegates to the *first failing sub-rule* via
  `build_child_exception`. For a nested `AllOf`, that delegation would
  correctly recurse into the inner `AllOf.build_exception()` and still
  surface the true failing rule's card — so nesting wouldn't break
  diagnostics the way it would for `AnyOf` — but it would still create
  needless extra object instances and an unnecessarily deep call chain on
  every evaluation. Flattening keeps `AllOf` consistent with `AnyOf` and
  avoids that overhead.
* **How It Works:**
  During `__init__`, every positional `rule` argument is inspected with
  `type(rule) is AllOf` (exact type match, not `isinstance`, so a
  deliberate `AllOf` subclass overriding behavior is never silently
  unwrapped). Matching instances contribute their own `.rules` directly
  instead of themselves, applied at every position in the argument list —
  not just the first — so both `(a & b) & c` and `c & (a & b)` flatten to
  the same `AllOf(a, b, c)`.
* **Applies Equally to Manual Construction:**
  This also fixes `AllOf(AllOf(a, b), c)` written by hand, not just
  operator-chained expressions.

---

## 3. Exception Card Design

* **Transparent Delegation:** Vends the exact child exception card of the
  failing sub-rule.
"""
