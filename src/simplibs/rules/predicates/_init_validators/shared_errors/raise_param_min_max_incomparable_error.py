from typing import Any
from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "InRange": {
        "min_label": "min_val",
        "max_label": "max_val",
        "example": "InRange(min_val=1, max_val=10)",
    },
}


def raise_param_min_max_incomparable_error(
    rule_name: str,
    min_val: Any,
    max_val: Any,
) -> None:
    """Unconditionally raise a ParamError (TypeError) for incomparable boundary types."""

    # 1. Prepare data from configuration based on the rule name
    config = _PARAM_CONFIG.get(
        rule_name,
        {
            "min_label": "min_val",
            "max_label": "max_val",
            "example": f"{rule_name}(1, 10)",
        },
    )

    min_label = config["min_label"]
    max_label = config["max_label"]

    # 2. Build and raise the exception
    raise ParamError(
        error_name="INCOMPARABLE_RANGE_BOUNDS_ERROR",
        label=f"{rule_name}.{min_label}/{max_label}",
        expected="comparable boundary types",
        value=(min_val, max_val),
        problem=f"Cannot compare boundary types '{type(min_val).__name__}' ({min_val!r}) and '{type(max_val).__name__}' ({max_val!r}).",
        how_to_fix=(
            f"Provide '{min_label}' and '{max_label}' of comparable types.",
            f"Example: {config['example']}",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_param_min_max_incomparable_error — Incomparable Range Boundaries Guard

## Purpose
Raises a `ParamError` (wrapping `TypeError`) when upper and lower boundaries
of a range rule cannot be compared due to incompatible data types.

---

## 1. Execution Rationale

* **Early Type Safety:**
  Catches boundary type mismatches (e.g., comparing `str` with `int`) at
  rule initialization time.
* **Contextual Diagnostic Formatting:**
  Embeds explicit class names of both boundary values into the `problem`
  field to assist quick debugging.
"""
