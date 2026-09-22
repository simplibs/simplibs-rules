from typing import Any, Container
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsContainer(Rule):
    """Value must be a valid non-string collection/container (e.g. list, tuple, set, dict).

    Rule:
        isinstance(value, (list, tuple, set, frozenset, dict)) or isinstance(value, Container)

    Example:
        validate(value, IsContainer())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # Exclude str and bytes, which do have __contains__ but are not
        # considered element collections here
        if isinstance(value, (str, bytes)):
            return False

        # Check for standard collections or an implementation of the Container protocol
        return isinstance(value, (list, tuple, set, frozenset, dict)) or isinstance(value, Container)

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        return ValidationError(
            error_name="IS_CONTAINER_ERROR",
            label=value_name,
            expected="a container collection (list, tuple, set, dict)",
            value=value,
            problem=f"Value {value!r} of type '{type(value).__name__}' is not a container.",
            context=context,
            how_to_fix="Provide a valid container collection.",
            exception=TypeError,
        )


# ----------------------------------------------------------------------
# Helper function for internal parameter validation in __init__
# ----------------------------------------------------------------------
is_container = IsContainer().is_valid


_DESIGN_NOTES = """
# IsContainer — Non-String Collection Validation Rule

## Purpose
The `IsContainer` rule validates that an input value is a non-string
collection/container (e.g., `list`, `tuple`, `set`, `frozenset`, `dict`, or
any custom type implementing the `Container` protocol).

---

## 1. Execution Rationale & Safeguards

* **String/Bytes Exclusion:**
  `str` and `bytes` technically implement `__contains__` (and thus the
  `Container` protocol), but are explicitly rejected first, since they
  represent scalar text data rather than collections of discrete elements.
* **Dual Detection Strategy:**
  Accepts either one of the standard built-in collection types directly, or
  any object satisfying the abstract `Container` protocol, allowing custom
  container-like classes to pass validation as well.

---

## 2. Ecosystem Integration

* **Internal `is_container` Helper:**
  Exposes `is_container = IsContainer().is_valid` as a bound-method
  shortcut at module level. This mirrors the pattern used elsewhere in the
  library (e.g., `is_integer`, `is_primitive_number`) so that other rule
  constructors (`IsSubsetOf`, `IsSupersetOf`) can perform a fast internal
  parameter check without instantiating a new `IsContainer()` each time.

---

## 3. Exception Card Design

* **Error Classification:** Uses `IS_CONTAINER_ERROR` wrapping a
  `TypeError`, since failing this rule always reflects a fundamental type
  mismatch rather than a value-range problem.
"""
