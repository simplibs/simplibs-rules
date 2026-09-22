from typing import Any, Callable
from simplibs.exception import ValidationError
# Outers
from ..base_class import Rule
# Inners
from ._helpers import as_predicate, describe_rule
from ._init_validators import raise_rule_param_not_callable


class Not(Rule):
    """Value must NOT satisfy the given rule or predicate.

    Rule:
        not rule(value)

    Example:
        validate(value, Not(IsNone()))
    """

    __slots__ = ("rule",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, rule: Callable[[Any], bool]) -> None:

        # 1. Parameter validation
        if not callable(rule):
            raise_rule_param_not_callable("Not", rule)

        # 2. Parameter assignment
        self.rule = rule

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value fails the wrapped rule
        return not as_predicate(self.rule)(value)

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
        description = describe_rule(self.rule)

        # 2. Build the exception
        return ValidationError(
            error_name="NOT_RULE_ERROR",
            label=value_name,
            expected=f"value NOT satisfying {description}",
            value=value,
            problem=f"Value unexpectedly satisfied forbidden rule/condition: {description}.",
            context=context,
            how_to_fix=(
                f"Provide a value that does not satisfy {description}.",
            ),
            exception=ValueError,
        )


_DESIGN_NOTES = """
# Not — Boolean Inversion Container Rule

## Purpose
The `Not` rule negates the logical output of an underlying child rule or
callable predicate function.

---

## 1. Execution Rationale & Constructor Protection

* **Constructor Guard:**
  Ensures the inner `rule` parameter is either a `Rule` instance or a
  callable object via `raise_rule_param_not_callable`.
* **Stateless Negation:**
  Inverts `as_predicate(self.rule)(value)` cleanly without storing internal
  failure flags or state.

---

## 2. Exception Card Design

* **Dynamic Rule Identification:**
  Uses `describe_rule(self.rule)` to embed the exact expectation or
  function name of the forbidden condition directly into `problem` and
  `how_to_fix`.
* **Error Classification:** Uses `NOT_RULE_ERROR` wrapping a `ValueError`.
"""
