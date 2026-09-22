from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsInteger(Rule):
    """Value must be an integer (not bool).

    Rule:
        isinstance(value, int) and not isinstance(value, bool)

    Example:
        validate(value, IsInteger())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is an int (excluding bool)
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not an integer."
        how_to_fix = "Provide an int value (booleans like True/False are excluded)."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_INTEGER_ERROR",
            label=value_name,
            expected="an integer",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


# ----------------------------------------------------------------------
# Helper functions for internal validation across the project
# ----------------------------------------------------------------------
is_integer = IsInteger().is_valid


def is_non_negative_integer(value: Any) -> bool:
    """Return True if the tested value satisfies the rule, otherwise False.

    Params:
        value: Any

    Return:
        bool
    """
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


_DESIGN_NOTES = """
# IsInteger — Strict Integer Validation Rule

## Purpose
The `IsInteger` rule validates that an input value is an `int`, explicitly
excluding `bool`.

---

## 1. Execution Rationale & Safeguards

* **Boolean Exclusion:**
  Evaluates `isinstance(value, int) and not isinstance(value, bool)` to
  prevent `True`/`False` from passing as integers.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_INTEGER_ERROR` wrapping a
  `TypeError`.
* **Fix Guidance:** Clarifies that booleans are excluded.

---

## 3. Ecosystem Integration

* **Internal `is_integer` / `is_non_negative_integer` Helpers:**
  Exposes `is_integer = IsInteger().is_valid` and a standalone
  `is_non_negative_integer()` at module level, mirroring the pattern used
  by other primitive-type rules (`is_number`, `is_primitive_number`,
  `is_container`). Other rule constructors (`HasLength`, `IsPi`,
  `DivisibleBy`, `HasRemainder`) import these for fast internal parameter
  checks without instantiating a new `IsInteger()` each time.

## Notes
* A previous revision left a broken draft (`is_non_negative_integer =
  deff(...)`) between two working definitions of this function. `deff`
  was never a real function, so importing this module would have raised
  `NameError` at import time, breaking the entire `numeric` sub-package.
  That dead/broken code has been removed; only the final, clean
  implementation remains.
"""
