from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsEven(Rule):
    """Value must be an even integer (not bool).

    Rule:
        isinstance(value, int) and not isinstance(value, bool) and value % 2 == 0

    Example:
        validate(value, IsEven())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value is an even integer (excluding bool)
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
            and value % 2 == 0
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
        # 1.1 When value is not an integer (or is a bool)
        if not isinstance(value, int) or isinstance(value, bool):
            problem = f"Value {value!r} of type '{type(value).__name__}' is not an integer."
            how_to_fix = "Provide an integer value (booleans like True/False are excluded)."
            exception_type = TypeError

        # 1.2 When the integer is odd
        else:
            problem = f"Value {value!r} is an odd integer."
            how_to_fix = "Provide an even integer (e.g. -2, 0, 4)."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_EVEN_ERROR",
            label=value_name,
            expected="an even integer",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsEven — Even Integer Validation Rule

## Purpose
The `IsEven` rule validates that an input value is an even integer,
explicitly excluding `bool` — same convention as `IsInteger` and every
other rule in `predicates/numeric/`.

---

## 1. Execution Rationale & Safeguards

* **Boolean Exclusion:**
  Evaluates `isinstance(value, int) and not isinstance(value, bool)`
  before the modulo check, so `True`/`False` never pass as "even"/"odd"
  by virtue of being `1`/`0` under the hood.
* **No Float Support, On Purpose:**
  `value % 2 == 0` is only meaningful for `int` — `4.0 % 2 == 0` is `True`
  in Python, but "evenness" is not a concept that generalizes cleanly to
  floats (rounding, precision). Compose with `IsInteger()` explicitly if
  a caller wants to *also* accept floats that happen to be integral —
  this rule intentionally stays narrow rather than guessing intent.

---

## 2. Relationship to `IsOdd`

`IsEven`/`IsOdd` are two independent rules, not one rule and its `Not()`
wrapped around the other — same reasoning as `IsBlank`/`NotBlank`:
independent implementation gives each a specific, direct diagnostic
message ("is an odd integer" vs. a generic "did not satisfy
Not(IsOdd())"), rather than deriving one from the other's negation.

---

## 3. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't an integer
  at all (mirrors `IsInteger`'s own message); `ValueError`
  (`IS_EVEN_ERROR`) when it is an integer, just an odd one.
"""
