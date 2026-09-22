from typing import Any, Literal
from simplibs.exception import ParamError


_PARAM_CONFIG: dict[str, dict[str, str]] = {
    "transformer": {
        "expected": "callable function or method",
        "example": "str.strip",
        "fix": "Provide a callable object that transforms an input value (e.g., str.strip or custom function).",
    },
    "validator": {
        "expected": "Rule instance or callable predicate",
        "example": "HasLength(min_=1)",
        "fix": "Provide a Rule instance or a function returning bool (e.g., HasLength(min_=1)).",
    },
}


def validate_compose_param_is_callable(
    param_name: Literal["transformer", "validator"],
    value: Any,
) -> None:
    """Check that the parameter is callable. If not, raise a tailored ParamError."""

    # 1. Fast happy-path guard
    if callable(value):
        return

    # 2. Prepare data
    config = _PARAM_CONFIG.get(
        param_name,
        {
            "expected": "callable object",
            "example": "lambda x: x",
            "fix": "Provide a valid callable object.",
        },
    )

    # 3. Build and raise the exception
    raise ParamError(
        error_name="COMPOSE_PARAM_NOT_CALLABLE_ERROR",
        label=f"Compose.{param_name}",
        expected=config["expected"],
        value=value,
        problem=f"Parameter '{param_name}' must be callable, but got '{type(value).__name__}'.",
        how_to_fix=(
            config["fix"],
            f"Example: Compose({config['example']}, ...)",
        ),
    )


_DESIGN_NOTES = """
# validate_compose_param_is_callable — Compose Rule Parameter Guard

## Purpose
Validates that `transformer` and `validator` parameters passed to `Compose`
are callable, providing tailored `ParamError` diagnostics via internal
configuration lookup.

---

## 1. Execution Rationale & Map-Based Lookup

* **Guard Logic:**
  Returns immediately if `callable(value)` evaluates to `True`, keeping
  happy-path overhead minimal.
* **Declarative Metadata:**
  Uses a `_PARAM_CONFIG` mapping dictionary to store exact `expected`,
  `example`, and `fix` strings per parameter, avoiding messy branching or
  repetitive boilerplate.
"""
