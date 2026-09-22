from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import (
    raise_param_missing_error,
    raise_param_not_type_error
)

class IsInstance(Rule):
    """Value must be an instance of the given type(s).

    Rule:
        isinstance(value, types)

    Example:
        validate(value, IsInstance(int))
        validate(value, IsInstance(int, float))
    """

    __slots__ = ("types",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *types: type) -> None:

        # 1. Check that at least one type was passed
        if not types:
            raise_param_missing_error("IsInstance")

        # 2. Check that all passed arguments are valid types
        for type_ in types:
            if not isinstance(type_, type):
                raise_param_not_type_error("IsInstance", "types", type_)

        # 3. Store parameters
        self.types = types

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the instance check
        return isinstance(value, self.types)

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
        names = ", ".join(t.__name__ for t in self.types)
        problem = f"Value {value!r} is of type '{type(value).__name__}', expected instance of ({names})."
        how_to_fix = f"Provide an instance of ({names})."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_INSTANCE_ERROR",
            label=value_name,
            expected=f"instance of ({names})",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsInstance — Type Instance Inspection Rule

## Purpose
The `IsInstance` rule validates that a target value is an instance of one
or more specified classes/types.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Verifies that at least one type argument is passed and validates that
  all passed parameters are valid class types (`isinstance(t, type)`),
  raising `ParamError` for missing or invalid inputs.
* **Variadic Type Support:**
  Accepts multiple target types (`*types`). Native Python
  `isinstance(value, tuple)` natively handles tuple-based checks with high
  performance.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_INSTANCE_ERROR` wrapping a
  `TypeError`.
* **Diagnostic Detail:** Explicitly formats the runtime type
  (`type(value).__name__`) and allowed types.
"""
