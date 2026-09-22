from typing import Any
from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "StartsWith.prefix": {
        "example": "StartsWith('https://')",
        "fix": "Provide a string prefix parameter.",
    },
    "EndsWith.suffix": {
        "example": "EndsWith('.py')",
        "fix": "Provide a string suffix parameter.",
    },
    "Contains.substring": {
        "example": "Contains('@')",
        "fix": "Provide a string substring parameter.",
    },
    "Regex.pattern": {
        "example": "Regex(r'^[a-z]+$')",
        "fix": "Provide a valid regex string pattern.",
    },
    "HasAttribute.attr_name": {
        "example": "HasAttribute('append')",
        "fix": "Provide a string attribute name parameter.",
    },
}


def raise_param_not_string_error(
    rule_name: str,
    param_name: str,
    value: Any,
) -> None:
    """Raise a ParamError (TypeError) when a parameter is not a string (str)."""

    # 1. Look up the specific config by rule and parameter name
    lookup_key = f"{rule_name}.{param_name}"
    config = _PARAM_CONFIG.get(
        lookup_key,
        {
            "example": f"{rule_name}({param_name}='...')",
            "fix": f"Provide a string for '{param_name}'.",
        },
    )

    # 2. Build and raise the exception
    raise ParamError(
        error_name="PARAM_NOT_TYPE_ERROR",
        label=lookup_key,
        expected="string",
        value=value,
        problem=f"Parameter '{param_name}' must be a str, got '{type(value).__name__}'.",
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_param_not_string_error — String Parameter Type Guard

## Purpose
Raises a `ParamError` (wrapping `TypeError`) when a string parameter is
required during rule instantiation but another data type is provided.

---

## 1. Execution Rationale

* **Type Safety Guard:**
  Enforces strictly string parameters for text and reflection rules
  (`StartsWith`, `EndsWith`, `Contains`, `Regex`, `HasAttribute`).
* **Configurable Remediation Messages:**
  Uses map-based lookups to provide exact string parameter examples based
  on the active rule context.
"""
