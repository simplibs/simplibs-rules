from collections.abc import Mapping
from typing import Any, Callable
from simplibs.exception import ValidationError
# Outers
from ..base_class import Rule
from ..predicates.introspection import IsInstance
# Inners
from ._helpers import as_predicate, build_child_exception, describe_rule, format_value_label
from .AllOf import AllOf
from .AnyOf import AnyOf
from .Compose import Compose
from ._init_validators import raise_rule_param_not_callable


class ForEachValue(Rule):
    """Every value of a mapping must satisfy the given rule.

    Rule:
        all(rule(item) for item in value.values())

    Example:
        validate(options, ForEachValue(IsInteger()))
    """

    __slots__ = ("rule",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, rule: Rule | Callable[[Any], bool]) -> None:

        # 1. Parameter validation
        if not callable(rule):
            raise_rule_param_not_callable("ForEachValue", rule)

        # 2. Parameter assignment
        self.rule = rule

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Only a mapping has values
        if not isinstance(value, Mapping):
            return False

        # 2. Evaluate the rule for every value
        predicate = as_predicate(self.rule)
        return all(predicate(item) for item in value.values())

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Compound operands need parentheses: each value: (a | b)
        return f"each value: {describe_rule(self.rule, parenthesize=(AllOf, AnyOf, Compose))}"

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. A value that is not a mapping fails on the mapping check
        if not isinstance(value, Mapping):
            return IsInstance(Mapping).build_exception(value, value_name, context)

        # 2. Find the first value that fails the rule and build a child exception
        predicate = as_predicate(self.rule)
        for key, item in value.items():
            if not predicate(item):
                return build_child_exception(
                    self.rule,
                    item,
                    format_value_label(key, value_name),
                    context,
                )

        # 3. Fallback (build exception if all values unexpectedly passed)
        return ValidationError(
            error_name="FOR_EACH_VALUE_UNREACHABLE_ERROR",
            label=value_name,
            expected="mapping with all values passing the rule",
            value=value,
            problem="All values unexpectedly passed during error construction.",
            context=context,
            how_to_fix=("Check mapping values state.",),
            exception=RuntimeError,
        )


_DESIGN_NOTES = """
# ForEachValue — Mapping Value Validation Container Rule

## Purpose
The `ForEachValue` rule applies a target validation rule or callable predicate
to every value of a mapping, and names a failing value by its KEY.

---

## 1. Why a Rule of Its Own

* **`ForEach` Cannot Say Which Entry Failed:**
  It knows only the position of an item (`opts[1]`). For `**kwargs: int` the
  person looks for the parameter by its name, not by its order.
* **`Compose(values, ForEach(...))` Throws the Keys Away:**
  The extraction step hands `ForEach` a bare view, so the key is gone before
  the exception is built. A rule that receives the mapping itself keeps it.
* **`ForEach` Is Not Changed:**
  Over a mapping it walks the keys by the iteration contract of Python;
  changing that would silently change every existing use.

---

## 2. Execution Rationale

* **Constructor Safety Guard:**
  Ensures the inner `rule` is either an instance of `Rule` or a callable
  object (`raise_rule_param_not_callable`).
* **Mapping Check:**
  `is_valid` returns `False` for anything that is not a `collections.abc.Mapping`.
* **Cheap Happy Path:**
  `is_valid` walks only `.values()`; the keys are needed (and `.items()`
  is used) only once a failure has to be reported.
* **Non-mapping Exception Delegation:**
  `build_exception` hands a non-mapping to `IsInstance(Mapping)`, so the card
  says what was expected instead of inventing a failing entry.
* **Empty Mapping:**
  Passes (`all()` over nothing is true), same as `ForEach` over an empty list.

---

## 3. Exception Card Design

* **Value Label:**
  The failing value is named through `format_value_label` — `opts['b']`, or
  `['b']` without a name — the spelling of the access in Python.
* **Transparent Sub-rule Delegation:**
  The card is the exact exception of the sub-rule for the failing value; its
  `value` is that value, not the whole mapping. A nested rule builds on the
  label (`opts['a'][1]`).
* **Unreachable Fallback:**
  `FOR_EACH_VALUE_UNREACHABLE_ERROR` when no value fails during error construction.

---

## 4. Description

* **Prefix Form:**
  `describe()` returns "each value: <rule>" ("each value: int").
* **Precedence:**
  A compound operand (`AllOf`, `AnyOf`, `Compose`) is wrapped in parentheses
  ("each value: (a | b)").
"""
