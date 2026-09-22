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


class NoneOf(Rule):
    """Value must satisfy none of the given rules.

    Rule:
        not any(rule(value) for rule in rules)

    Example:
        validate(value, NoneOf(IsZero(), IsNone()))
    """

    __slots__ = ("rules",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *rules: Rule | Callable[[Any], bool]) -> None:

        # 1. Parameter validation
        if not rules:
            raise_requires_at_least_one_rule_error("NoneOf")

        for rule in rules:
            if not callable(rule):
                raise_rule_param_not_callable("NoneOf", rule)

        # 2. Parameter assignment
        self.rules = rules

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value satisfies none of the given rules
        return not any(as_predicate(rule)(value) for rule in self.rules)

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
        matched = [
            describe_rule(rule)
            for rule in self.rules
            if as_predicate(rule)(value)
        ]

        all_rules_desc = ", ".join(describe_rule(r) for r in self.rules)
        matched_desc = ", ".join(matched) if matched else "one or more rules"

        # 2. Build the exception
        return ValidationError(
            error_name="NONE_OF_ERROR",
            label=value_name,
            expected=f"value satisfying none of: {all_rules_desc}",
            value=value,
            problem=f"Value unexpectedly satisfied forbidden rule(s): {matched_desc}.",
            context=context,
            how_to_fix=(
                f"Modify the value so that it does not match any of: {all_rules_desc}.",
            ),
            exception=ValueError,
        )


_DESIGN_NOTES = """
# NoneOf — Negative Composite Container Rule

## Purpose
The `NoneOf` rule ensures that an input value satisfies **none** of the
specified child rules or predicate functions.

---

## 1. Execution Rationale & Direct Evaluation

* **Direct Evaluation (Variant A Rationale):**
  Avoids wrapper delegation to `Not(AnyOf(...))` to keep the happy-path
  `is_valid` call stack shallow, eliminate redundant object creation, and
  achieve optimal performance.
* **Constructor Safeguard:**
  Requires at least one argument via
  `raise_requires_at_least_one_rule_error("NoneOf")`.

---

## 2. Exception Card Design

* **Matched Rule Breakdown:**
  `build_exception` explicitly identifies and names which specific rule(s)
  were unexpectedly matched by `value`, providing crystal-clear diagnostic
  information in the `problem` section.
* **Error Classification:** Uses `NONE_OF_ERROR` wrapping a `ValueError`.
"""
