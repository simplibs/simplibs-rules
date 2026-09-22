from typing import Any, Callable
from simplibs.exception import ValidationError
# Outers
from ..base_class import Rule
# Inners
from ._helpers import as_predicate, describe_rule
from ._init_validators import (
    raise_requires_at_least_one_rule_error,
    raise_rule_param_not_callable
)


class AnyOf(Rule):
    """Value must satisfy at least one of the given rules.

    Rule:
        any(rule(value) for rule in rules)

    Example:
        validate(value, AnyOf(IsInteger(), IsFloat()))
        validate(value, IsInteger() | IsFloat())
    """

    __slots__ = ("rules",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *rules: Rule | Callable[[Any], bool]) -> None:

        # 1. Parameter validation
        if not rules:
            raise_requires_at_least_one_rule_error("AnyOf")

        # 2. Flatten nested AnyOf instances (e.g. from `a | b | c` chaining)
        #    into a single flat rule list, rather than nesting AnyOf(AnyOf(...), ...)
        flattened: list[Rule | Any] = []
        for rule in rules:
            if not callable(rule):
                raise_rule_param_not_callable("AnyOf", rule)
            if type(rule) is AnyOf:
                flattened.extend(rule.rules)
            else:
                flattened.append(rule)

        # 3. Parameter assignment
        self.rules = tuple(flattened)

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value satisfies at least one rule
        return any(
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

        # 1. Prepare data
        descriptions = ", ".join(describe_rule(rule) for rule in self.rules)

        # 2. Build the exception
        return ValidationError(
            error_name="ANY_OF_ERROR",
            label=value_name,
            expected=f"value satisfying at least one of: {descriptions}",
            value=value,
            problem=f"Value did not satisfy any of: {descriptions}.",
            context=context,
            how_to_fix=(
                f"Provide a value that satisfies at least one of: {descriptions}.",
            ),
            exception=ValueError,
        )


_DESIGN_NOTES = """
# AnyOf — Logical OR Container Validation Rule

## Purpose
The `AnyOf` rule aggregates multiple validation rules or callables,
requiring an input value to satisfy AT LEAST ONE contained rule (logical
disjunction / OR). It is also the rule constructed under the hood by
`Rule.__or__`/`Rule.__ror__` (`rule1 | rule2`).

---

## 1. Execution Rationale & Short-Circuit Evaluation

* **Constructor Fail-Fast:**
  Guards against empty rule sets on instantiation via
  `raise_requires_at_least_one_rule_error` (`ParamError`).
* **Short-Circuit Evaluation:**
  Uses Python's native `any()` to short-circuit upon encountering the first
  passing rule.
* **Composite Error Aggregation:**
  Since all rules fail when `build_exception` is reached, `AnyOf` aggregates
  string descriptions of all sub-rules via `describe_rule`.

---

## 2. Self-Flattening Constructor

* **Why It's Needed:**
  `Rule.__or__` builds `AnyOf` instances one pair at a time, so a chained
  expression like `a | b | c` evaluates left-to-right as `(a | b) | c`,
  which — without flattening — would construct a nested
  `AnyOf(AnyOf(a, b), c)` rather than a flat `AnyOf(a, b, c)`.
* **Why Nesting Would Be a Problem:**
  `build_exception` calls `describe_rule(rule)` for every sub-rule to list
  candidate requirements. `describe_rule` on a nested `AnyOf` instance
  returns only `"AnyOf"` (its class name), producing an unreadable
  diagnostic like *"expected one of: AnyOf, IsFloat"* instead of
  *"expected one of: IsInteger, IsFloat, IsFloat"* — a real regression in
  diagnostic quality, not just cosmetic nesting.
* **How It Works:**
  During `__init__`, every positional `rule` argument is inspected with
  `type(rule) is AnyOf` (exact type match, not `isinstance`, so a
  deliberate `AnyOf` subclass overriding behavior is never silently
  unwrapped). Matching instances contribute their own `.rules` directly
  instead of themselves, applied at every position in the argument list —
  not just the first — so both `(a | b) | c` and `c | (a | b)` flatten to
  the same `AnyOf(a, b, c)`.
* **Applies Equally to Manual Construction:**
  This also fixes `AnyOf(AnyOf(a, b), c)` written by hand, not just
  operator-chained expressions.

---

## 3. Exception Card Design

* **Error Classification:** Uses `ANY_OF_ERROR` wrapping a `ValueError`.
* **Summary Listing:** Concatenates rule descriptions to form a transparent
  overview of candidate requirements.
"""
