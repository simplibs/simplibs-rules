from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsString(Rule):
    """Value must be a string.

    Rule:
        isinstance(value, str)

    Example:
        validate(value, IsString())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is a string
        return isinstance(value, str)

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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not a string."
        how_to_fix = "Provide a str value."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_STRING_ERROR",
            label=value_name,
            expected="a string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


# ----------------------------------------------------------------------
# Helper functions for internal validation across the project
# ----------------------------------------------------------------------
is_string = IsString().is_valid


def is_non_empty_string(value: Any) -> bool:
    """Return True if the tested value is a non-empty string, otherwise False.

    Params:
        value: Any

    Return:
        bool
    """
    return isinstance(value, str) and bool(value.strip())


_DESIGN_NOTES = """
# IsString — Strict String Validation Rule

## Purpose
The `IsString` rule validates that an input value is an instance of `str`.

---

## 1. Execution Rationale & Safeguards

* **Type Check:**
  Evaluates `isinstance(value, str)` to ensure the value is a standard Python
  string instance.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_STRING_ERROR` wrapping a `TypeError`.
* **Fix Guidance:** Clarifies that a string (`str`) value must be provided.

---

## 3. Ecosystem Integration

* **Internal `is_string` / `is_non_empty_string` Helpers:**
  Exposes `is_string = IsString().is_valid` and a standalone
  `is_non_empty_string()` at module level, mirroring the pattern used
  by other primitive-type rules (`is_integer`, `is_number`). Other rule
  constructors import these for fast internal parameter checks without
  instantiating a new `IsString()` each time.
"""