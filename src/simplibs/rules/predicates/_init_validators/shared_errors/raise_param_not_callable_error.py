from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_param_not_callable_error(
    rule_name: str,
    param_name: str,
    value: Any,
) -> NoReturn:
    """Raise a ParamError when a parameter expected to be a callable is not callable.

    Args:
        rule_name: Name of the rule class (e.g. "UserRule").
        param_name: Name of the parameter (e.g. "rule").
        value: The invalid non-callable value received.

    Raises:
        ParamError: Always.
    """
    raise ParamError(
        error_name="PARAM_NOT_CALLABLE_ERROR",
        label=f"{rule_name}.{param_name}",
        expected="a callable object (function, lambda, or predicate)",
        value=value,
        problem=(
            f"Parameter '{param_name}' of '{rule_name}' must be a callable, "
            f"got '{type(value).__name__}'."
        ),
        how_to_fix=(
            f"Provide a valid function or lambda to '{rule_name}'.",
            f"Example: {rule_name}(lambda v: v > 0)",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_param_not_callable_error — Shared Non-Callable Parameter Guard

## Purpose
Raises a standardized `ParamError` when a constructor parameter requires a callable
predicate or function, but receives a non-callable object.

---

## 1. Execution Rationale

* **Reusable Diagnostic Card:**
  Serves any predicate rule requiring callable parameters (such as `UserRule`),
  providing multi-line tuple-formatted error cards and code examples.
"""