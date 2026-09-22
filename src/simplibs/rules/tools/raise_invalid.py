from typing import Any, Callable, NoReturn
from simplibs.exception import build_validation_error
# Inners
from ..base_class import Rule


def raise_invalid(
    value: Any,
    rule: Rule | Callable[[Any], bool],
    *,
    value_name: str | None = None,
    context: str | None = None,
) -> NoReturn:
    """Unconditionally raise a validation exception associated with the given rule.

    This function does not evaluate the truthiness of the rule (`is_valid` / callable is not called).
    It serves as a direct shortcut for scenarios where conditional code has already verified a failure,
    and the sole objective is to construct and raise the corresponding `ValidationError`.

    Args:
        value: The value that failed validation.
        rule: A rule instance (`Rule`) or callable object used to construct the exception.
        value_name: The name of the validated parameter/variable for diagnostic reporting.
        context: Additional context describing the validation failure.

    Raises:
        ValidationError: Always raises the exception constructed by the rule or fallback factory.
    """

    # 1. Rule instance handling
    if isinstance(rule, Rule):
        raise rule.build_exception(
            value,
            value_name=value_name,
            context=context,
        )

    # 2. Callable handling (plain function / lambda)
    raise build_validation_error(
        rule,
        value,
        value_name=value_name,
        context=context,
    )


_DESIGN_NOTES = """
# raise_invalid — Unconditional Validation Exception Trigger

## Purpose
The `raise_invalid()` function provides a direct shortcut for raising
structured validation exceptions without re-evaluating conditions. It is
designed for the "happy path" pattern where control flow guards have already
detected a failure condition inline.

---

## 1. Execution Pipeline

1. **Bypassing Evaluation Logic:**
   * Unlike `validate()`, this function **never calls** `rule(value)` or
     `rule.is_valid(value)`.
   * It assumes the calling context has already determined validation
     failure.

2. **Exception Construction & Dispatch:**
   * **`isinstance(rule, Rule)`:** Delegates exception construction to
     `rule.build_exception()`.
   * **Callable / Lambda:** Delegates construction to the universal fallback
     factory `build_validation_error()`.
   * The resulting exception is raised immediately (`NoReturn`).

---

## 2. Design Choices & Rationale

### Semantic Distinction from `validate()`
* Using `validate()` makes sense when the developer wants the library to
  evaluate the condition and trigger errors automatically.
* Using `raise_invalid()` is ideal under an `if not condition:` block,
  explicitly communicating intent: *"The condition has already been checked;
  now assemble and raise the diagnostic error card."*
* Avoids double-executing potentially expensive rule logic.
"""