from typing import Any
from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "IsSubclass.types": {
        "example": "IsSubclass(BaseClass)",
        "fix": "Provide valid class types (objects of type 'type').",
    },
    "IsInstance.types": {
        "example": "IsInstance(int, str)",
        "fix": "Provide valid class types (objects of type 'type').",
    },
}


def raise_param_not_type_error(
    rule_name: str,
    param_name: str,
    value: Any,
) -> None:
    """Raise a ParamError (TypeError) when a parameter is not a 'type' object (class)."""

    # 1. Look up the specific config by rule and parameter name
    lookup_key = f"{rule_name}.{param_name}"
    config = _PARAM_CONFIG.get(
        lookup_key,
        {
            "example": f"{rule_name}(MyClass)",
            "fix": f"Provide a valid class type for '{param_name}'.",
        },
    )

    # 2. Build and raise the exception
    raise ParamError(
        error_name="PARAM_NOT_TYPE_ERROR",
        label=lookup_key,
        expected="type (class)",
        value=value,
        problem=f"Parameter '{param_name}' must be a type (class), got '{type(value).__name__}'.",
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_param_not_type_error — Class Type Parameter Guard

## Purpose
Raises a `ParamError` (wrapping `TypeError`) when a rule parameter expects
a Python class type object (`type`) but receives a non-class value.

---

## 1. Execution Rationale

* **Metaclass Type Safety:**
  Guards introspection rules (`IsSubclass`, `IsInstance`) from invalid
  non-type arguments passed at construction time.
* **Clean Configuration Lookup:**
  Retrieves context-aware error text dynamically using
  `{rule_name}.{param_name}` lookup keys.
"""
