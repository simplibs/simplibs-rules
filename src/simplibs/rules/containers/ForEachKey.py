from collections.abc import Mapping
from typing import Any, Callable
from simplibs.exception import ValidationError
# Outers
from ..base_class import Rule
from ..predicates.introspection import IsInstance
# Inners
from ._helpers import as_predicate, build_child_exception, describe_rule, format_key_label
from .AllOf import AllOf
from .AnyOf import AnyOf
from .Compose import Compose
from ._init_validators import raise_rule_param_not_callable


class ForEachKey(Rule):
    """Every key of a mapping must satisfy the given rule.

    Rule:
        all(rule(key) for key in value.keys())

    Example:
        validate(options, ForEachKey(IsString()))
    """

    __slots__ = ("rule",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, rule: Rule | Callable[[Any], bool]) -> None:

        # 1. Parameter validation
        if not callable(rule):
            raise_rule_param_not_callable("ForEachKey", rule)

        # 2. Parameter assignment
        self.rule = rule

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Only a mapping has keys
        if not isinstance(value, Mapping):
            return False

        # 2. Evaluate the rule for every key
        predicate = as_predicate(self.rule)
        return all(predicate(key) for key in value.keys())

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Compound operands need parentheses: each key: (a | b)
        return f"each key: {describe_rule(self.rule, parenthesize=(AllOf, AnyOf, Compose))}"

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

        # 2. Find the first key that fails the rule and build a child exception
        predicate = as_predicate(self.rule)
        for key in value.keys():
            if not predicate(key):
                return build_child_exception(
                    self.rule,
                    key,
                    format_key_label(key, value_name),
                    context,
                )

        # 3. Fallback (build exception if all keys unexpectedly passed)
        return ValidationError(
            error_name="FOR_EACH_KEY_UNREACHABLE_ERROR",
            label=value_name,
            expected="mapping with all keys passing the rule",
            value=value,
            problem="All keys unexpectedly passed during error construction.",
            context=context,
            how_to_fix=("Check mapping keys state.",),
            exception=RuntimeError,
        )


_DESIGN_NOTES = """
# ForEachKey — Mapping Key Validation Container Rule

## Purpose
The `ForEachKey` rule applies a target validation rule or callable predicate
to every key of a mapping.

---

## 1. Why a Rule of Its Own

* **`ForEach` Cannot Say Which Entry Failed:**
  It knows only the position of an item (`opts[1]`), not what the entry is
  called. For a mapping the name is what a person looks for.
* **`Compose(keys, ForEach(...))` Throws the Mapping Away:**
  The extraction step hands `ForEach` a bare view, so the information about
  the entry is gone before the exception is built. A rule that receives the
  mapping itself keeps it until the end.
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
* **Non-mapping Exception Delegation:**
  `build_exception` hands a non-mapping to `IsInstance(Mapping)`, so the card
  says what was expected instead of inventing a failing key.
* **Empty Mapping:**
  Passes (`all()` over nothing is true), same as `ForEach` over an empty list.

---

## 3. Exception Card Design

* **Key Label:**
  The failing key is named through `format_key_label` — `opts[key 'zz']`, or
  `[key 'zz']` without a name. The word `key` keeps it apart from the label of
  a value (`opts['zz']`).
* **Transparent Sub-rule Delegation:**
  The card is the exact exception of the sub-rule for the failing key; its
  `value` is the key, not the whole mapping.
* **Unreachable Fallback:**
  `FOR_EACH_KEY_UNREACHABLE_ERROR` when no key fails during error construction.

---

## 4. Description

* **Prefix Form:**
  `describe()` returns "each key: <rule>" ("each key: str").
* **Precedence:**
  A compound operand (`AllOf`, `AnyOf`, `Compose`) is wrapped in parentheses
  ("each key: (a | b)").
"""
