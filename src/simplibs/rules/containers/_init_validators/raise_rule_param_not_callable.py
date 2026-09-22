from typing import Any, Literal
from simplibs.exception import ParamError


def raise_rule_param_not_callable(
    rule_name: Literal["AllOf", "AnyOf", "NoneOf", "ForEach", "Not"] | str,
    rule_param: Any,
) -> None:
    """Check that the child rule is callable/Rule. If not, raise a ParamError."""

    # 1. Prepare data
    examples = {
        "ForEach": "IsInteger()",
        "Not": "IsNone()",
        "AllOf": "IsInteger(), GreaterThan(0)",
        "AnyOf": "IsInteger(), IsFloat()",
        "NoneOf": "IsZero(), IsNone()",
    }
    example = examples.get(rule_name, "IsInteger()")

    # 2. Build and raise the exception
    raise ParamError(
        error_name="SINGLE_RULE_PARAM_NOT_CALLABLE_ERROR",
        label=f"{rule_name}.rule",
        expected="Rule instance or callable predicate",
        value=rule_param,
        problem=(
            f"Rule '{rule_name}' requires a Rule instance or callable predicate, "
            f"got '{type(rule_param).__name__}'."
        ),
        how_to_fix=(
            f"Provide a valid Rule instance or a function returning bool (e.g., {rule_name}({example})).",
        ),
    )


_DESIGN_NOTES = """
# raise_rule_param_not_callable — Container Single-Rule Parameter Guard

## Purpose
Enforces that single-rule container classes (`ForEach`, `Not`) receive a
valid `Rule` instance or callable predicate upon instantiation.

---

## 1. Execution Rationale

* **Fast Guard:**
  Returns immediately if `callable(rule_param)` is `True`, keeping
  happy-path instantiation overhead down to a single C-API check.
* **Contextual Examples:**
  Dynamically provides relevant code examples (`IsInteger()` for `ForEach`,
  `IsNone()` for `Not`) based on `rule_name`.
"""
