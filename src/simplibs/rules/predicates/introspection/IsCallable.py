from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsCallable(Rule):
    """Value must be callable.

    Rule:
        callable(value)

    Example:
        validate(value, IsCallable())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the object is callable
        return callable(value)

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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not callable."
        how_to_fix = "Provide a callable (function, method, lambda, or object implementing __call__)."
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_CALLABLE_ERROR",
            label=value_name,
            expected="callable object",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsCallable — Callable Object Inspection Rule

## Purpose
The `IsCallable` rule evaluates whether an input value can be invoked as a
function using Python's native `callable()` check.

---

## 1. Execution Rationale & Safeguards

* **Native Python Inspection:**
  Relies directly on built-in `callable(value)`. Handles functions,
  methods, classes, lambdas, and instances with `__call__` defined.
* **Zero Exception Overhead:**
  The `callable()` predicate never raises exceptions in Python, ensuring
  exception-free execution inside `is_valid`.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_CALLABLE_ERROR` wrapping a
  `TypeError`.
* **Fix Guidance:** Lists explicit valid callable forms (functions,
  methods, objects with `__call__`).
"""
