from typing import Any
from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "CloseTo.target": {
        "expected": "primitive number (int or float)",
        "example": "CloseTo(10.0, rel_tol=1e-3)",
        "fix": "Provide a primitive target number (int or float).",
    },
    "CloseTo.rel_tol": {
        "expected": "primitive number (int or float)",
        "example": "CloseTo(10.0, rel_tol=1e-3)",
        "fix": "Provide a relative tolerance value (int or float).",
    },
    "CloseTo.abs_tol": {
        "expected": "primitive number (int or float)",
        "example": "CloseTo(10.0, abs_tol=0.5)",
        "fix": "Provide an absolute tolerance value (int or float).",
    },
}


def validate_param_is_primitive_number(
    rule_name: str,
    param_name: str,
    value: Any,
) -> None:
    """Check that a parameter is a primitive number (int or float, excluding bool)."""

    # 1. Fast primitive-numeric-type check (happy-path guard)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return

    # 2. Prepare data from configuration
    config = _PARAM_CONFIG.get(
        f"{rule_name}.{param_name}",
        {
            "expected": "int or float",
            "example": f"{rule_name}(10.5)",
            "fix": "Provide a primitive number (int or float; booleans excluded).",
        },
    )

    # 3. Build and raise the exception
    raise ParamError(
        error_name="PARAM_NOT_TYPE_ERROR",
        label=f"{rule_name}.{param_name}",
        expected=config["expected"],
        value=value,
        problem=f"Parameter '{param_name}' must be a primitive number (int or float), got '{type(value).__name__}'.",
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=TypeError
    )


_DESIGN_NOTES = """
# validate_param_is_primitive_number — Primitive Numeric Type Guard

## Purpose
Validates that a constructor parameter is a primitive numeric type (`int`
or `float`) while explicitly rejecting booleans (`bool`).

---

## 1. Execution Rationale

* **Primitive Numeric Validation:**
  Ensures inputs strictly conform to numeric types suitable for standard
  math operations, preventing boolean coercion.
* **Map-Based Configuration:**
  Provides precise diagnostic strings for rules like `CloseTo` and its
  tolerance parameters.
"""
