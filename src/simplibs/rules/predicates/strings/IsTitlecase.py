from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...base_class import Rule


class IsTitlecase(Rule):
    """String value must be title-cased.

    Rule:
        value.istitle()

    Example:
        validate(value, IsTitlecase())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the type and title-case content
        return (

            # 1.1 Check that the value is of type str
            isinstance(value, str)

            # 1.2 Check that each word starts with an uppercase letter,
            #     with all remaining cased characters lowercase
            and value.istitle()
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

        # 1.2 When the string is not title-cased
        else:
            problem = f"Value {value!r} is not title-cased."
            how_to_fix = "Provide a string where each word starts with an uppercase letter (e.g. 'Hello World')."
            exception_type = ValueError

        # 2. Build the exception
        return ValidationError(
            error_name="IS_TITLECASE_ERROR",
            label=value_name,
            expected="a title-cased string",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsTitlecase — Title-Case String Validation Rule

## Purpose
The `IsTitlecase` rule validates that a string is title-cased (each word
begins with an uppercase letter, remaining letters lowercase), via
Python's native `str.istitle()`.

---

## 1. Execution Rationale & Safeguards

* **No At-Least-One-Letter Special-Casing:**
  Unlike `IsLowercase`/`IsUppercase`, `str.istitle()` already returns
  `False` for a string with no cased characters (`"123".istitle()` is
  `False`), so no extra reasoning is needed here beyond what the
  standard library already does — noted for completeness, not because
  anything unusual had to be handled.

---

## 2. Shared Shape Across `IsAlpha`/`IsAlnum`/`IsDigitString`/`IsAscii`/
`IsLowercase`/`IsUppercase`/`IsTitlecase` — One Consolidated Note

All seven of these rules share the exact same shape:

```python
def is_valid(self, value: Any) -> bool:
    return isinstance(value, str) and value.<method>()
```

Each was still written as its own full `Rule` subclass — its own file,
its own `build_exception`, its own `_DESIGN_NOTES` — rather than
generated from one shared factory (e.g. `_build_str_method_rule("istitle",
error_name="IS_TITLECASE_ERROR", ...)`), for the same reason every other
predicate in this library gets its own file: each rule is independently
discoverable (`from simplibs.rules.presets import is_titlecase`),
independently documented, and produces its own specific, named exception
(`IS_TITLECASE_ERROR`, not a generic "string method check failed").

**This is flagged as a real, open trade-off, not settled either way.** A
factory function would remove seven near-identical class bodies and
reduce the chance of a copy-paste slip between them (this batch was in
fact copy-pasted from `IsAlpha` and adjusted per-rule) — at the cost of
each rule's `build_exception`/error name becoming *generated* rather than
directly readable in its own file, and losing the one place a rule-
specific docstring/design-note naturally lives. Worth revisiting if an
eighth or ninth sibling of this exact shape shows up (`str.isnumeric()`,
`str.isdecimal()`, `str.isspace()`, `str.isprintable()` are the next
obvious candidates) — at that point the duplication cost likely outweighs
the discoverability benefit, and a factory becomes the better trade.

---

## 3. Exception Card Design

* **Dual Diagnostic Path:** `TypeError` when the value isn't a string at
  all; `ValueError` (`IS_TITLECASE_ERROR`) when it is a string but isn't
  title-cased.
"""
