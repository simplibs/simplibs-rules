from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsOdd(Rule):
    """Value must be an odd integer (not bool).

    Rule:
        isinstance(value, int) and not isinstance(value, bool) and value % 2 != 0

    Example:
        validate(value, IsOdd())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is an odd integer (excluding bool)
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
            and value % 2 != 0
        )

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Prepare data
        # 1.1 When value is not an integer (or is a bool)
        if not isinstance(value, int) or isinstance(value, bool):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not an integer."
            how_to_fix = "Provide an integer value (booleans like True/False are excluded)."
            exception_type = TypeError

        # 1.2 When the integer is even
        else:
            problem = f"Value {value!r} is an even integer."
            how_to_fix = "Provide an odd integer (e.g. -3, 1, 5)."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_ODD_ERROR",
            label=value_name,
            expected="an odd integer",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsOdd — Odd Integer Validation Rule

## Purpose
The `IsOdd` rule validates that an input value is an odd integer,
explicitly excluding `bool` — the mirror image of `IsEven`, implemented
independently rather than as `Not(IsEven())` for the same reason `IsBlank`
and `NotBlank` are both independently implemented: a direct, specific
diagnostic ("is an even integer") beats a generic negated one.

---

## 1. Execution Rationale & Safeguards

* **Boolean Exclusion:** Same guard as `IsEven`, `IsInteger`, and every
  other rule in `predicates/numeric/` — `True`/`False` are never treated
  as `1`/`0` for this check.
* **No Float Support, On Purpose:** Same reasoning as `IsEven` — oddness
  is only a well-defined concept for `int`.

---

## 2. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't an integer
  at all; `ValueError` (`IS_ODD_ERROR`) when it is an integer, just an
  even one.
"""
