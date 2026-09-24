from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsIdentifier(Rule):
    """String value must be a valid Python identifier.

    Rule:
        value.isidentifier()

    Example:
        validate(value, IsIdentifier())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and identifier validity
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that the value is a valid Python identifier
            and value.isidentifier()
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
        # 1.1 When value is not a string
        if not isinstance(value, str):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not a string."
            how_to_fix = "Provide a string value."
            exception_type = TypeError

        # 1.2 When the string is not a valid Python identifier
        else:
            problem = f"Value {value!r} is not a valid Python identifier."
            how_to_fix = "Provide a valid Python identifier string (e.g. 'my_var', 'foo1')."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_IDENTIFIER_ERROR",
            label=value_name,
            expected="a valid Python identifier string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


# ----------------------------------------------------------------------
# Helper function for internal validation across the project
# ----------------------------------------------------------------------
is_identifier = IsIdentifier().is_valid


_DESIGN_NOTES = """
# IsIdentifier — Python Identifier Validation Rule

## Purpose
The `IsIdentifier` rule validates that a string is a valid Python identifier
via Python's native `str.isidentifier()`.

---

## 1. Execution Rationale & Safeguards

* **Unicode-Aware:**
  `str.isidentifier()` follows Python 3 rules for valid identifiers, including
  Unicode characters valid in variable names.
* **Empty String & Keywords:**
  `"".isidentifier()` returns `False`. Python language keywords (like `def`, `class`)
  return `True` under `str.isidentifier()`.

---

## 2. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at all;
  `ValueError` (`IS_IDENTIFIER_ERROR`) when it is a string but fails the identifier check.
"""