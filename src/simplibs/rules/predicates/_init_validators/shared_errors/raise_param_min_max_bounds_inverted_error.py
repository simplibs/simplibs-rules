from typing import Any
from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "HasLength": {
        "min_label": "min_length",
        "max_label": "max_length",
        "expected": "min_length <= max_length",
        "example": "HasLength(min_length=1, max_length=10)",
        "fix": "Ensure min_length is less than or equal to max_length.",
    },
    "InRange": {
        "min_label": "min_val",
        "max_label": "max_val",
        "expected": "min_val <= max_val",
        "example": "InRange(min_val=1, max_val=10)",
        "fix": "Ensure min_val is less than or equal to max_val.",
    },
}


def raise_param_min_max_bounds_inverted_error(
    rule_name: str,
    min_val: Any,
    max_val: Any,
) -> None:
    """Unconditionally raise a ParamError (ValueError) for inverted bounds (min > max)."""

    # 1. Prepare data from configuration based on the rule name
    config = _PARAM_CONFIG.get(
        rule_name,
        {
            "min_label": "min_val",
            "max_label": "max_val",
            "expected": "min_val <= max_val",
            "example": f"{rule_name}(min_val=1, max_val=10)",
            "fix": "Ensure minimum boundary is less than or equal to maximum boundary.",
        },
    )

    min_label = config["min_label"]
    max_label = config["max_label"]

    # 2. Build and raise the exception
    raise ParamError(
        error_name="BOUNDS_INVERTED_ERROR",
        label=f"{rule_name}.{min_label}",
        expected=f"{config['expected']} ({min_label}={min_val!r}, {max_label}={max_val!r})",
        value=(min_val, max_val),
        problem=f"Parameter '{min_label}' ({min_val!r}) cannot be greater than '{max_label}' ({max_val!r}).",
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_param_min_max_bounds_inverted_error — Inverted Range Boundaries Guard

## Purpose
Raises a `ParamError` (wrapping `ValueError`) when range boundaries are
inverted during rule instantiation (e.g., `min_val > max_val` or
`min_length > max_length`).

---

## 1. Execution Rationale & Map-Based Lookup

* **Fail-Fast Boundary Guard:**
  Ensures that invalid logical ranges are caught during constructor
  initialization.
* **Declarative Parameter Mapping:**
  Uses `_PARAM_CONFIG` to map rule-specific parameter names
  (`min_length`/`max_length` vs `min_val`/`max_val`) to build accurate
  error messages.
"""
