from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_user_rule_param_wrong_arity(rule_name: str, rule: Any) -> NoReturn:
    """Raise a ParamError when a UserRule's callable cannot accept exactly
    one positional value.

    Args:
        rule_name: The Rule class name for the diagnostic message.
        rule: The invalid callable.

    Raises:
        ParamError: Always.
    """
    callable_desc = getattr(rule, "__name__", repr(rule))

    raise ParamError(
        error_name="RULE_PARAM_WRONG_ARITY_ERROR",
        label=f"{rule_name}.rule",
        expected="a callable accepting exactly one positional argument 'value'",
        value=rule,
        problem=(
            f"The callable '{callable_desc}' supplied to '{rule_name}' cannot be called with a single positional value.",
            "It requires zero, multiple mandatory positional arguments, or mandatory keyword-only parameters.",
        ),
        how_to_fix=(
            f"Provide a callable that accepts exactly one positional argument to receive the value being validated.",
            f"Example: {rule_name}(lambda v: v > 0)",
            f"Or with default parameters: {rule_name}(lambda v, limit=10: v < limit)",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_user_rule_param_wrong_arity — UserRule Arity Violation Guard

## Purpose
Raises a tailored `ParamError` at rule construction time when a callable provided
to `UserRule` structurally cannot accept a single positional argument `rule(value)`.

---

## 1. Execution Rationale

* **Fail-Fast Signature Diagnostics:**
  Prevents invalid callables (e.g., `lambda: True` or `lambda a, b: a + b`) from
  failing silently during `is_valid()` execution where exceptions are caught.
* **Tuple-Formatted Multi-Line Diagnostic Messages:**
  Uses structured `tuple` sequences for `problem` and `how_to_fix` fields to format
  clear, multi-line error cards with concrete code examples.
"""