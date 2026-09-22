from simplibs.exception import ParamError


def raise_requires_at_least_one_rule_error(rule_name: str) -> None:
    """Raise a ParamError when a container was initialized without any rules."""

    # 1. Build and raise the exception
    raise ParamError(
        error_name="REQUIRES_AT_LEAST_ONE_RULE_ERROR",
        label=f"{rule_name}.*rules",
        expected="at least one rule or predicate argument",
        value=None,
        problem=f"Rule '{rule_name}' requires at least one rule to evaluate.",
        how_to_fix=(
            f"Pass at least one Rule or callable function to '{rule_name}' (e.g., {rule_name}(IsInteger())).",
        ),
    )


_DESIGN_NOTES = """
# raise_requires_at_least_one_rule_error — Empty Rule List Guard

## Purpose
Raises a `ParamError` when a composite/container rule (such as `NoneOf`,
`AnyOf`, `AllOf`) is instantiated without passing any rule arguments.

---

## 1. Execution Rationale

* **Fail-Fast Initialization:**
  Prevents instantiation of logical containers that have no underlying
  rules to evaluate, avoiding ambiguous runtime behavior.
* **Reusable Across Composite Rules:**
  Accepts `rule_name` dynamically to serve `NoneOf`, `AnyOf`, `AllOf`, and
  other variadic composite containers.
"""
