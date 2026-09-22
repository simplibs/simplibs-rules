from typing import Any
from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "HasLength.length": {
        "example": "HasLength(length=5)",
        "fix": "Provide a non-negative integer for exact length match.",
    },
    "HasLength.min_length": {
        "example": "HasLength(min_length=1)",
        "fix": "Provide a non-negative integer for minimum length boundary.",
    },
    "HasLength.max_length": {
        "example": "HasLength(max_length=10)",
        "fix": "Provide a non-negative integer for maximum length boundary.",
    },
    "IsPi.decimal_places": {
        "example": "IsPi(decimal_places=5)",
        "fix": "Provide a non-negative integer for decimal places precision.",
    },
    "DivisibleBy.divisor": {
        "example": "DivisibleBy(divisor=5)",
        "fix": "Provide a non-negative integer for division.",
    },
}


def raise_param_not_non_negative_integer_error(
    rule_name: str,
    param_name: str,
    value: Any,
) -> None:
    """Raise a ParamError when a parameter is not a non-negative integer (int >= 0)."""

    # 1. Look up the specific config with a fallback to generic text
    lookup_key = f"{rule_name}.{param_name}"
    config = _PARAM_CONFIG.get(
        lookup_key,
        {
            "example": f"{rule_name}({param_name}=5)",
            "fix": f"Provide a valid non-negative integer for '{param_name}'.",
        },
    )

    # 2. Distinguish the exact cause (wrong type vs. negative value)
    if not isinstance(value, int) or isinstance(value, bool):
        expected_desc = "non-negative integer (int)"
        problem_desc = f"Parameter '{param_name}' must be an integer, got '{type(value).__name__}'."
        exc_type = TypeError
    else:
        expected_desc = "integer greater than or equal to 0"
        problem_desc = f"Parameter '{param_name}' must be non-negative (>= 0), got {value}."
        exc_type = ValueError

    # 3. Raise the exception
    raise ParamError(
        error_name="PARAM_NOT_NON_NEGATIVE_INT_ERROR",
        label=lookup_key,
        expected=expected_desc,
        value=value,
        problem=problem_desc,
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=exc_type,
    )


_DESIGN_NOTES = """
# raise_param_not_non_negative_integer_error — Non-Negative Integer Guard

## Purpose
Raises a `ParamError` when a rule constructor parameter requires a
non-negative integer (`int >= 0`) but receives an invalid type or negative
value.

---

## 1. Execution Rationale & Precise Fault Branching

* **Dual Fault Classification:**
  Distinguishes between type mismatches (`TypeError` for non-ints/bools) and
  boundary violations (`ValueError` for negative ints).
* **Explicit Boolean Safeguard:**
  Treats `bool` inputs explicitly as non-integers despite Python's `bool`
  subclassing `int`.
"""
