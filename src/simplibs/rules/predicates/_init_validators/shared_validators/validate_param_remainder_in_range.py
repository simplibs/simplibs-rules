from simplibs.exception import ParamError

_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "remainder": {
        "expected": "remainder in range 0 <= remainder < |divisor|",
        "example": "HasRemainder(divisor=5, remainder=2)",
        "fix": "Ensure remainder is non-negative and strictly less than the absolute value of divisor.",
    },
}


def validate_param_remainder_in_range(
    rule_name: str,
    divisor: int,
    remainder: int,
) -> None:
    """Check that the remainder falls within the mathematically valid range 0 <= remainder < |divisor|."""

    # 1. Fast mathematical-range check for the remainder (happy-path guard)
    if 0 <= remainder < abs(divisor):
        return

    # 2. Prepare data from configuration
    config = _PARAM_CONFIG["remainder"]

    # 3. Build and raise the exception
    raise ParamError(
        error_name="REMAINDER_OUT_OF_RANGE_ERROR",
        label=f"{rule_name}.remainder",
        expected=f"0 <= remainder < {abs(divisor)}",
        value=remainder,
        problem=f"Parameter 'remainder' ({remainder}) must be between 0 and {abs(divisor) - 1} for divisor {divisor}.",
        how_to_fix=(
            config["fix"],
            f"Example: {config['example']}",
        ),
        exception=ValueError
    )


_DESIGN_NOTES = """
# validate_param_remainder_in_range — Remainder Bounds Guard

## Purpose
Ensures that a specified integer remainder satisfies the mathematical
constraint `0 <= remainder < |divisor|` relative to the given divisor.

---

## 1. Execution Rationale

* **Mathematical Validity Verification:**
  Evaluates boundaries using `abs(divisor)` to guarantee valid modulus
  ranges regardless of whether the divisor is positive or negative.
* **Clear Boundary Feedback:**
  Includes the calculated allowed range (`0` to `abs(divisor) - 1`) directly
  in the exception's `problem` message.
"""
