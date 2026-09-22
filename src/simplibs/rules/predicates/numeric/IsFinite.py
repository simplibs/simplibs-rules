import math
from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsFinite(Rule):
    """Value must be a primitive number (int or float, excluding bool) that is
    neither NaN nor infinite.

    Rule:
        isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

    Example:
        validate(value, IsFinite())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate type, boolean exclusion, and finiteness
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
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
        # 1.1 When value is not a primitive number
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not a primitive number (int, float)."
            how_to_fix = "Provide a primitive numeric value (int or float; booleans excluded)."
            exception_type = TypeError

        # 1.2 When the number is NaN or infinite
        else:
            problem = f"Value {value!r} is not finite (NaN or infinite)."
            how_to_fix = "Provide a finite numeric value (not NaN, not +/-inf)."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_FINITE_ERROR",
            label=value_name,
            expected="a finite number (not NaN, not infinite)",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsFinite — Finite Number Validation Rule

## Purpose
The `IsFinite` rule validates that an input value is a primitive number
(`int`/`float`, `bool` excluded) that is neither NaN nor +/-infinity.

---

## 1. Execution Rationale & Safeguards

* **`math.isfinite` Over Manual Negation:**
  `negate(is_nan) & negate(is_infinity)` would express the same
  constraint by composing two existing rules, but `math.isfinite(value)`
  is one direct, well-known standard-library check — clearer at the call
  site (`IsFinite()` vs. a two-part composed negation) and avoids two
  function calls plus two `Not` wrapper allocations for what is
  conceptually a single question ("is this a normal, usable number?").
* **Boolean Exclusion Before `math.isfinite`:**
  `math.isfinite(True)` would itself return `True` (bool coerces to
  `1`), so the explicit `not isinstance(value, bool)` guard runs first —
  same convention as every other rule in this sub-package.
* **`int` Is Always Finite; `math.isfinite` Handles It Directly:**
  Python's `int` has no NaN/infinity representation, so this rule is only
  ever meaningfully restrictive for `float` input — `int` values always
  pass once they clear the type/bool checks, and `math.isfinite` accepts
  `int` natively (no manual branching needed to special-case it).

---

## 2. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a primitive
  number at all (mirrors `IsPrimitiveNumber`'s own message); `ValueError`
  (`IS_FINITE_ERROR`) when it is one, just not finite.
"""
