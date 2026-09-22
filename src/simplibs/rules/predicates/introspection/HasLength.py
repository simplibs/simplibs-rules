from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule
from ..numeric.IsInteger import is_non_negative_integer
from .._init_validators import (
    raise_param_not_non_negative_integer_error,
    raise_param_min_max_bounds_inverted_error,
    raise_param_missing_error,
    raise_has_length_param_conflict_error,
)


class HasLength(Rule):
    """Value's length must equal `length`, or fall within [min_length, max_length].

    Rule:
        value == length
        value > min_length
        value < max_length
        min_length < value < max_length

    Example:
        validate(value, HasLength(length=10))
        validate(value, HasLength(min_length=1))
        validate(value, HasLength(max_length=10))
        validate(value, HasLength(min_length=1, max_length=10))
    """

    __slots__ = ("length", "min_length", "max_length")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(
        self,
        length: int | None = None,
        *,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:

        # 1. No parameter at all was provided
        if length is None and min_length is None and max_length is None:
            raise_param_missing_error("HasLength")

        # 2. Validate exact length mode (mode 1)
        if length is not None:
            if min_length is not None or max_length is not None:
                raise_has_length_param_conflict_error(length, min_length, max_length)

            if not is_non_negative_integer(length):
                raise_param_not_non_negative_integer_error("HasLength", "length", length)

        # 3. Validate length range mode (mode 2)
        else:
            if min_length is not None and not is_non_negative_integer(min_length):
                raise_param_not_non_negative_integer_error("HasLength", "min_length", min_length)

            if max_length is not None and not is_non_negative_integer(max_length):
                raise_param_not_non_negative_integer_error("HasLength", "max_length", max_length)

            if min_length is not None and max_length is not None and min_length > max_length:
                raise_param_min_max_bounds_inverted_error("HasLength", min_length, max_length)

        # 4. Store parameters
        self.length = length
        self.min_length = min_length
        self.max_length = max_length

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the object's length
        try:
            length = len(value)
        except TypeError:
            return False

        # 2. Check the exact length
        if self.length is not None:
            return length == self.length

        # 3. Check the minimum boundary
        if self.min_length is not None and length < self.min_length:
            return False

        # 4. Check the maximum boundary
        if self.max_length is not None and length > self.max_length:
            return False

        # 5. Report successful validation
        return True

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        expected = self._describe_expected()

        # 1. Prepare data
        # 1.1 When value has no defined length (is not Sized)
        try:
            length = len(value)
            problem = f"Value has length {length}, expected {expected}."
            how_to_fix = f"Provide a value with {expected}."
            exception_type = ValueError
        except TypeError:
            problem = f"Value {value!r} of type '{type(value).__name__}' has no len()."
            how_to_fix = f"Provide a sized collection (e.g. list, str, tuple) with {expected}."
            exception_type = TypeError

        # 2. Build the exception
        return ValidationError(
            error_name="HAS_LENGTH_ERROR",
            label=value_name,
            expected=expected,
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )

    def _describe_expected(self) -> str:
        if self.length is not None:
            return f"length {self.length}"
        if self.min_length is not None and self.max_length is not None:
            return f"length between {self.min_length} and {self.max_length}"
        if self.min_length is not None:
            return f"length at least {self.min_length}"
        return f"length at most {self.max_length}"


_DESIGN_NOTES = """
# HasLength — Collection Length Validation Rule

## Purpose
The `HasLength` rule evaluates whether a container's length (`len(value)`)
meets target conditions: an exact target (`length`) or boundary conditions
(`min_length` and/or `max_length`).

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Directly validates that input bounds are non-negative integers
  (`is_non_negative_integer`) and checks parameter compatibility (`length`
  vs `min_length`/`max_length`, missing bounds, `min_length > max_length`),
  raising `ParamError` for invalid configurations.
* **Runtime Type Safety (`is_valid`):**
  Uses `try/except TypeError` during `len(value)` evaluation to safely
  return `False` for non-sized objects.
* **Dual Diagnostic Path (`build_exception`):**
  Uses `try/except TypeError` on `len(value)` to assemble:
  * A `TypeError` when the evaluated input is not sized (lacks `__len__`).
  * A `ValueError` (`HAS_LENGTH_ERROR`) when the collection length falls
    outside target bounds.

---

## 2. Exception Card Design

* **Type Failures:** Non-sized inputs format problem/fix strings as
  `TypeError`.
* **Value Failures:** Invalid length collections format problem/fix
  strings as `ValueError` (`HAS_LENGTH_ERROR`).
"""