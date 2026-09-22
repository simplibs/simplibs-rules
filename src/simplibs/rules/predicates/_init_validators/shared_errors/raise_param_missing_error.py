from typing import Any
from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, Any]] = {
    "HasLength.missing": {
        "expected": "at least one constraint (length, min_length, or max_length)",
        "example": "HasLength(length=5) or HasLength(min_length=1, max_length=10)",
        "fix": "Provide 'length', 'min_length', or 'max_length' parameter.",
    },
    "IsSubclass.missing": {
        "expected": "at least one type argument",
        "example": "IsSubclass(BaseClass) or IsSubclass(ClassA, ClassB)",
        "fix": "Provide one or more base classes as arguments.",
    },
    "IsInstance.missing": {
        "expected": "at least one type argument",
        "example": "IsInstance(int) or IsInstance(int, float)",
        "fix": "Provide one or more target types as arguments.",
    },
    "HasKeys.keys": {
        "expected": "at least one key argument",
        "example": "HasKeys('id', 'name')",
        "fix": "Provide at least one key to check.",
    },
}


def raise_param_missing_error(
    rule_name: str,
    key_suffix: str = "missing",
) -> None:
    """Raise a ParamError when none of the required parameters were provided."""

    # 1. Prepare data and build the dictionary lookup key
    lookup_key = f"{rule_name}.{key_suffix}"
    config = _PARAM_CONFIG.get(
        lookup_key,
        {
            "expected": "at least one required parameter",
            "example": f"{rule_name}(...)",
            "fix": "Provide at least one required parameter for this rule.",
        },
    )

    # 2. Build and raise the exception
    raise ParamError(
        error_name="PARAM_MISSING_ERROR",
        label=rule_name,
        expected=config["expected"],
        value=None,
        problem=f"Rule '{rule_name}' requires at least one parameter constraint.",
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_param_missing_error — Missing Mandatory Rule Parameter Guard

## Purpose
Raises a `ParamError` (wrapping `ValueError`) when a rule constructor is
invoked without any required constraint or argument.

---

## 1. Execution Rationale & Config Lookup

* **Flexible Lookup Key:**
  Uses a composite key (`{rule_name}.{key_suffix}`) to select rule-specific
  diagnostic strings for missing parameter configurations.
* **Reusable Error Abstraction:**
  Centralizes missing argument error creation across multiple rules
  (`HasLength`, `IsSubclass`, `IsInstance`, `HasKeys`).
"""
