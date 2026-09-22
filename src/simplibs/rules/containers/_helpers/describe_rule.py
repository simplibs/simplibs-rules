from typing import Any, Callable
# Outers
from ...base_class import Rule


def describe_rule(
    rule: Rule | Callable[[Any], bool]
) -> str:
    """Return a readable name for a rule or function, for use in error messages."""

    # 1. Handling for a formal Rule instance
    if isinstance(rule, Rule):
        return type(rule).__name__

    # 2. Handling for a user-defined rule
    return getattr(rule, "__name__", repr(rule))


_DESIGN_NOTES = """
# describe_rule — Rule Representation Extraction Helper

## Purpose
Provides a standardized, concise string representation for validation rules
and callables to be embedded in composite error messages.

---

## 1. Execution Rationale

* **Rule Instance Branching:**
  Returns `type(rule).__name__` for formal `Rule` instances (e.g.,
  `"IsInteger"`).
* **Callable Fallback:**
  Safely extracts `__name__` or falls back to `repr(rule)` for raw functions
  or anonymous lambdas.

---

## 2. Why `Rule` Doesn't Get Its Own `__name__` Attribute

Defining a `__name__` attribute directly on the base `Rule` class would gain
essentially nothing in speed, and would add unnecessary architectural
complexity.

### Performance comparison

* **`isinstance(rule, Rule)` check:** Extremely fast in Python. It resolves
  via the object's internal type pointer (a C-level struct field) and takes
  on the order of a fraction of a microsecond.
* **`getattr(rule, "__name__", ...)` call:** Somewhat slower, since Python
  has to perform a dynamic lookup in the object's `__dict__` and, on
  failure, raise (and internally catch) an `AttributeError` before falling
  back to `repr(rule)`.

### Why adding `__name__` to `Rule` wouldn't pay off

1. **Rule diversity:** Not every rule has a unique name derivable purely
   from its class name. Some rules (e.g., `Regex(r"^\\d+$")` or
   `IsGreaterThan(5)`) carry specific parameters that `describe_rule` should
   ideally surface, whereas `type(rule).__name__` only returns the generic
   class name.
2. **It wouldn't help with plain callables:** Half of the inputs to `rule`
   can be plain functions (`lambda x: x > 0`), bound methods, or custom
   callable objects (instances implementing `__call__`) that have no
   `__name__` attribute at all. The branch would still be needed regardless.
3. **Separation of concerns:** Formatting logic for error messages and
   descriptions (`describe_rule`) belongs in diagnostic helper utilities,
   not in the base contract class `Rule`.

The current `isinstance`-based implementation is optimal both in terms of
performance and code cleanliness.
"""
