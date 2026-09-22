from typing import Any, Container

# Outers
from ...base_class import Rule
from simplibs.exception import ValidationError
from ..collections.IsContainer import is_container
from .._init_validators import raise_param_not_container_error
from .._helpers import format_container


class NotIn(Rule):
    """Value must NOT be a member of the given collection.

    Rule:
        value not in options

    Example:
        validate(value, NotIn(("banned", "forbidden")))
        validate(value, NotIn([0], strict=True))
    """

    __slots__ = ("options", "strict")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, options: Container[Any], strict: bool = False) -> None:

        # 1. Handle invalid input type error
        if not is_container(options):
            raise_param_not_container_error("NotIn", "options", options)

        # 2. Store parameters
        self.options = options
        self.strict = strict

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate absence from the collection
        try:
            if not self.strict:
                return value not in self.options

            # 2. Strict type check (exact type matching alongside value equality)
            target_type = type(value)
            return all(
                type(opt) is not target_type or opt != value
                for opt in self.options
            )

        # 3. Fallback for incomparable input
        except TypeError:
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

        # 1. Format the collection representation deterministically
        opts_repr = format_container(self.options)
        if len(opts_repr) > 60:
            opts_repr = f"{type(self.options).__name__}(size={len(self.options)})"

        # 2. Prepare data
        try:
            # Test comparability/hashability
            _ = value in self.options

            # 2.1 The value IS in the collection (or matches both value and type in strict mode)
            problem = f"Value {value!r} is forbidden — it appears in {opts_repr}."
            how_to_fix = f"Provide a value that is not present in {opts_repr}."
            exception_type = ValueError

        except TypeError:
            # 2.2 The value is unhashable
            problem = (
                f"Value {value!r} of type '{type(value).__name__}' cannot be checked "
                f"against container '{type(self.options).__name__}'."
            )
            how_to_fix = "Provide a hashable value or a compatible container."
            exception_type = TypeError

        # 3. Build the exception
        return ValidationError(
            error_name="NOT_IN_ERROR",
            label=value_name,
            expected=f"value not in {opts_repr}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# NotIn — Negative Collection Membership Rule

## Purpose
The `NotIn` rule verifies that a given input value is **not** present
within a collection of forbidden options.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Restricts `options` to standard collection data structures (`list`,
  `tuple`, `set`, `frozenset`, `dict`), throwing `ParamError` for
  non-container types.
* **Strict Type Enforcement (`strict=True`):**
  When `strict=False` (default), standard Python membership semantics apply
  (`True == 1`). When `strict=True`, presence requires both value equality
  (`==`) and exact type identity (`type(opt) is type(value)`), matching the
  mirror behavior of `IsIn`.
* **TypeError Safety (`is_valid`):**
  Uses a `try/except TypeError` block to return `True` when unhashable or
  incompatible types are checked against the container (since an
  unhashable value cannot be inside a set/dict, it satisfies `not in`).
* **Deterministic Set Representation:**
  Uses a helper `format_container` function during exception building to sort
  set elements before string formatting. This eliminates non-deterministic hash
  ordering when `set` or `frozenset` options are provided.
* **Representation Truncation:**
  If the container string representation exceeds 60 characters,
  `build_exception()` abbreviates it (`size=N`) to keep diagnostic output
  readable.

---

## 2. Exception Card Design

* **Error Classification:** Uses `NOT_IN_ERROR` wrapping a `ValueError`.
* **Fix Guidance:** Clear instruction to supply a value absent from the
  specified forbidden list.
"""