from typing import Any
from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "IsIn.options": {
        "example": "IsIn(['draft', 'published'])",
        "fix": "Provide a container parameter (list, tuple, set, frozenset, dict).",
    },
    "NotIn.options": {
        "example": "NotIn(['banned', 'forbidden'])",
        "fix": "Provide a container parameter (list, tuple, set, frozenset, dict).",
    },
    "IsSubsetOf.reference": {
        "example": "IsSubsetOf({'admin', 'user'})",
        "fix": "Provide a reference container for subset check.",
    },
    "IsSupersetOf.reference": {
        "example": "IsSupersetOf({'read', 'write'})",
        "fix": "Provide a reference container for superset check.",
    },
}


def raise_param_not_container_error(
    rule_name: str,
    param_name: str,
    value: Any,
) -> None:
    """Raise a ParamError (TypeError) when a parameter is not a valid container / collection."""

    # 1. Prepare data and look up the configuration for the rule and parameter
    lookup_key = f"{rule_name}.{param_name}"
    config = _PARAM_CONFIG.get(
        lookup_key,
        {
            "example": f"{rule_name}(['value1', 'value2'])",
            "fix": f"Provide a valid container parameter for '{param_name}'.",
        },
    )

    # 2. Build and raise the exception
    raise ParamError(
        error_name="PARAM_NOT_CONTAINER_ERROR",
        label=lookup_key,
        expected="container (list, tuple, set, frozenset, dict)",
        value=value,
        problem=f"Parameter '{param_name}' must be a container, got '{type(value).__name__}'.",
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_param_not_container_error — Container Type Parameter Guard

## Purpose
Raises a `ParamError` (wrapping `TypeError`) when a constructor parameter
expects a container collection (e.g., `list`, `set`, `tuple`) but receives
an invalid type.

---

## 1. Execution Rationale

* **Fail-Fast Collection Guard:**
  Ensures container-based rules (`IsIn`, `NotIn`, `IsSubsetOf`,
  `IsSupersetOf`) fail immediately during instantiation if passed
  non-container targets.
* **Declarative Mapping:**
  Maps rule and parameter names to exact usage examples and remediation
  guidance via `_PARAM_CONFIG`.
"""
