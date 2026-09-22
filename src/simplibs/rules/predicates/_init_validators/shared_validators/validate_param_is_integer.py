from typing import Any
from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "DivisibleBy.divisor": {
        "example": "DivisibleBy(divisor=5)",
        "fix": "Provide an non-zero integer divisor.",
    },
    "HasRemainder.divisor": {
        "example": "DivisibleBy(divisor=5)",
        "fix": "Provide an non-zero integer divisor.",
    },
    "HasRemainder.remainder": {
        "example": "HasRemainder(divisor=5, remainder=2)",
        "fix": "Provide an integer remainder.",
    },
}


def validate_param_is_integer(
    rule_name: str,
    param_name: str,
    value: Any,
) -> None:
    """Check that a parameter is of type int (excluding bool)."""

    # 1. Fast type-validity check (happy-path guard)
    if isinstance(value, int) and not isinstance(value, bool):
        return

    # 2. Prepare data based on the lookup key
    lookup_key = f"{rule_name}.{param_name}"
    config = _PARAM_CONFIG.get(
        lookup_key,
        {
            "example": f"{rule_name}(5)",
            "fix": "Provide an integer value (booleans are excluded).",
        },
    )

    # 3. Build and raise the exception
    raise ParamError(
        error_name="PARAM_NOT_TYPE_ERROR",
        label=lookup_key,
        expected="non-zero integer",
        value=value,
        problem=f"Parameter '{param_name}' must be an int, got '{type(value).__name__}'.",
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=TypeError
    )


_DESIGN_NOTES = """
# validate_param_is_integer — Strict Integer Constructor Guard

## Purpose
Validates that a constructor parameter is strictly an integer (`int`)
while explicitly rejecting booleans (`bool`).

---

## 1. Execution Rationale

* **Strict Type Checking:**
  Evaluates `isinstance(value, int)` and explicitly excludes `bool` to
  prevent implicit Python boolean-to-int coercion (e.g., `True` as `1`).
* **Declarative Mapping:**
  Maps `rule_name` and `param_name` combinations to targeted remediation
  strings via `_PARAM_CONFIG`.
"""
