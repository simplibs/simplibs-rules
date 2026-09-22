from typing import Any, NoReturn
from simplibs.exception import ValidationError


def raise_container_param_not_type_error(
    rule_name: str,
    param_name: str,
    value: Any,
    expected_type: str,
    example_usage: str | None = None,
) -> NoReturn:
    """Raise an exception when a rule constructor parameter does not have the expected type."""

    # 1. Prepare data
    fix_msg = f"Pass a valid {expected_type} to '{param_name}'."
    if example_usage:
        fix_msg += f" Example: {rule_name}({example_usage})"

    # 2. Build and raise the exception
    raise ValidationError(
        error_name="INVALID_PARAMETER_TYPE",
        label=param_name,
        expected=expected_type,
        value=value,
        problem=(
            f"Parameter '{param_name}' in rule '{rule_name}' must be {expected_type}, "
            f"got '{type(value).__name__}' ({value!r})."
        ),
        context=f"Initialization of rule '{rule_name}'",
        how_to_fix=(fix_msg,),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_container_param_not_type_error — Constructor Parameter Type Guard

## Purpose
Universal helper for fail-fast type checking within container rule
constructors (`__init__`).

---

## 1. Execution Rationale

* **Fail-Fast Safeguard:**
  Ensures that invalid parameter types passed during rule instantiation
  raise a structured `ValidationError` (wrapping `TypeError`) immediately.
* **Dynamic Diagnostic Composition:**
  Dynamically builds contextual `how_to_fix` instructions incorporating
  example usages when provided.
"""
