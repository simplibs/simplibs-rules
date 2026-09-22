from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "DivisibleBy.divisor": {
        "expected": "non-zero integer",
        "example": "DivisibleBy(divisor=5)",
        "fix": "Provide an integer divisor other than zero.",
    },
    "HasRemainder.divisor": {
        "expected": "non-zero integer",
        "example": "HasRemainder(divisor=5)",
        "fix": "Provide an integer divisor other than zero.",
    },
}


def validate_param_is_not_zero(
    rule_name: str,
    param_name: str,
    value: int | float,
) -> None:
    """Check that the divisor is not equal to 0."""

    # 1. Fast zero-value check (happy-path guard)
    if value != 0:
        return

    # 2. Prepare data from configuration
    config = _PARAM_CONFIG.get(
        f"{rule_name}.{param_name}",
        {
            "expected": "non-zero value",
            "example": f"{rule_name}(1)",
            "fix": "Provide a non-zero parameter.",
        },
    )

    # 3. Build and raise the exception
    raise ParamError(
        error_name="PARAM_CANNOT_BE_ZERO_ERROR",
        label=f"{rule_name}.{param_name}",
        expected=config["expected"],
        value=value,
        problem=f"Parameter '{param_name}' cannot be zero.",
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=ValueError
    )


_DESIGN_NOTES = """
# validate_param_is_not_zero — Non-Zero Value Constructor Guard

## Purpose
Ensures numeric constructor parameters (such as mathematical divisors) are
non-zero to prevent zero-division errors during rule evaluation.

---

## 1. Execution Rationale

* **Division-by-Zero Safeguard:**
  Fails fast at rule instantiation when `value == 0` is detected.
* **Contextual Diagnostic Strings:**
  Retrieves tailored expectation and fix messages dynamically using
  composite `{rule_name}.{param_name}` keys.
"""
