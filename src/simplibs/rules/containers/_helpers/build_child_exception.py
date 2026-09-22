from typing import Any, Callable
from simplibs.exception import build_validation_error
# Outers
from ...base_class import Rule


def build_child_exception(
    rule: Rule | Callable[[Any], bool],
    value: Any,
    value_name: str | None = None,
    context: str | None = None,
) -> Exception:
    """Delegate exception construction to the rule, or build a fallback ValidationError for a callable."""

    # 1. Handling for a formal Rule instance
    if isinstance(rule, Rule):
        return rule.build_exception(value, value_name, context)

    # 2. Handling for a user-defined rule
    return build_validation_error(rule, value, value_name, context)


_DESIGN_NOTES = """
# build_child_exception — Child Exception Delegation Helper

## Purpose
Provides unified exception construction for container rules containing
child rules or callable predicates.

---

## 1. Execution Rationale & Fallback Handling

* **Rule Polymorphism:**
  Calls `.build_exception(...)` if the child is a formal `Rule` instance.
* **Callable Fallback:**
  Uses `build_validation_error` to build a generic `ValidationError` card when
  the child is a raw function/lambda.
"""
