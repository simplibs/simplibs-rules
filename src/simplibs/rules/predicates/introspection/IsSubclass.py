from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from .._init_validators import (
    raise_param_missing_error,
    raise_param_not_type_error
)


class IsSubclass(Rule):
    """Value must be a subclass of the given type(s).

    Rule:
        issubclass(value, types)

    Example:
        validate(bool, IsSubclass(int))
        validate(MyClass, IsSubclass(BaseClass1, BaseClass2))
    """

    __slots__ = ("types",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *types: type) -> None:

        # 1. Check that at least one type was passed
        if not types:
            raise_param_missing_error("IsSubclass")

        # 2. Check that all passed arguments are valid types
        for type_ in types:
            if not isinstance(type_, type):
                raise_param_not_type_error("IsSubclass", "types", type_)

        # 3. Store parameters
        self.types = types

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is a class and a subclass of the expected types
        return (
            isinstance(value, type)
            and issubclass(value, self.types)
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

        names = ", ".join(t.__name__ for t in self.types)

        # 1. Prepare data
        # 1.1 When value is not a class at all (it's an instance)
        if not isinstance(value, type):
            problem = f"Value {value!r} is an instance of '{type(value).__name__}', not a class object."
            how_to_fix = f"Provide a class object itself (e.g. ({names})) instead of an instance."
            expected = f"a class (subclass of ({names}))"
        else:
            # 1.2 Value is a class, but doesn't inherit from the required class
            problem = f"Class '{value.__name__}' is not a subclass of ({names})."
            how_to_fix = f"Provide a class that inherits from ({names})."
            expected = f"subclass of ({names})"

        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_SUBCLASS_ERROR",
            label=value_name,
            expected=expected,
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsSubclass — Class Hierarchy Inspection Rule

## Purpose
The `IsSubclass` rule verifies that a target value is a Python class
(`type`) and inherits from one or more specified base classes.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Verifies that at least one type argument is passed and validates that
  all passed parameters are valid class types (`isinstance(t, type)`),
  raising `ParamError` for missing or invalid inputs.
* **Safe Traversal:**
  Guards via `isinstance(value, type)` before invoking `issubclass()`,
  preventing native `TypeError` when evaluating instances in predicate
  mode.

---

## 2. Exception Card Design

* **Dual Diagnostic Path:**
  - **Non-class Input:** Detects instances passed instead of class objects
    and provides tailored resolution instructions.
  - **Hierarchy Failure:** Formats the target class name and expected base
    class hierarchy.
* **Error Classification:** Uses `IS_SUBCLASS_ERROR` wrapping a
  `TypeError`.
"""
