from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsIterable(Rule):
    """Value must be iterable.

    Rule:
        iter(value)

    Example:
        validate(value, IsIterable())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate iterability using the built-in iter() function
        try:
            iter(value)
            return True

        # 2. Fallback for non-iterable input
        except TypeError:
            return False

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
        problem = f"Value {value!r} of type '{type(value).__name__}' is not iterable."
        how_to_fix = (
            "Provide an iterable object (e.g. list, tuple, set, dict, generator, or string)."
        )
        exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_ITERABLE_ERROR",
            label=value_name,
            expected="iterable value",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsIterable — Iterable Object Inspection Rule

## Purpose
The `IsIterable` rule validates whether an input value can be iterated over
using Python's native `iter()` protocol.

---

## 1. Execution Rationale & Safeguards

* **Protocol Compliance:**
  Executes `iter(value)` inside a targeted `try/except TypeError` block.
  This guarantees support for standard iterables (`list`, `tuple`, `dict`,
  `set`, `generator`, `str`) as well as sequence objects implementing
  legacy `__getitem__`.
* **Cross-Rule Reuse:**
  Serves as the central delegate for container rules (such as `ForEach`)
  when reporting non-iterable runtime input errors.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_ITERABLE_ERROR` wrapping a
  `TypeError`.
* **Fix Guidance:** Lists specific common Python iterable types.
"""
