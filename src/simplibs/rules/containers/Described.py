from typing import Any, Callable
# Outers
from ..base_class import Rule
# Inners
from ._helpers import as_predicate, build_child_exception
from ._init_validators import raise_rule_param_not_callable


class Described(Rule):
    """Behave exactly like the wrapped rule, but describe it with a fixed text.

    Rule:
        rule(value)

    Example:
        Described(AllOf(IsInstance(list), ForEach(IsInstance(int))), "list[int]")
    """

    __slots__ = ("rule", "text")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(
        self,
        rule: Rule | Callable[[Any], bool],
        text: str
    ) -> None:

        # 1. Parameter validation
        if not callable(rule):
            raise_rule_param_not_callable("Described", rule)

        # 2. Parameter assignment
        self.rule = rule
        self.text = text

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Delegate entirely to the wrapped rule
        return as_predicate(self.rule)(value)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. The fixed text replaces whatever the wrapped rule would say
        return self.text

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Delegate to the wrapped rule — it knows which part failed
        return build_child_exception(self.rule, value, value_name, context)


_DESIGN_NOTES = """
# Described — Fixed-Description Rule Wrapper

## Purpose
Wraps a rule so that `is_valid()` and `build_exception()` behave exactly as
before, while `describe()` returns a fixed text. It exists for rule trees
whose structure no longer reads like what the user wrote: `list[int]`
decomposes into `AllOf(IsInstance(list), ForEach(IsInstance(int)))`, which
would describe itself as "list & each int". `build_typing_rule` wraps such
trees with the annotation's own spelling ("list[int]").

---

## 1. Why a Wrapper, Not an Attribute on the Rule

* **Shared Instances Must Not Be Mutated:**
  A Rule used directly as an annotation, or the `_IS_ANY` singleton, is
  shared. Setting a description on it would leak into every other place
  that uses it.
* **Slots:**
  Rules declare `__slots__`, so an extra attribute on arbitrary rules is not
  possible without touching every class.

---

## 2. Not Flattened by AllOf / AnyOf

The containers flatten only exact `AllOf` / `AnyOf` instances
(`type(rule) is AllOf`). A `Described` is neither, so a described tree stays
one operand and keeps its text.

---

## 3. Transparent Diagnostics

`build_exception` delegates to the wrapped rule, so the failure card still
names the exact failing sub-rule. Only the *summary* text used by
containers (`describe()`) changes.

---

## 4. Cost

One extra method call per validation for every wrapped node. Plain item
types (`list[int]`) are not wrapped, so their per-item checks are untouched.
Nested generics are (`list[list[int]]`: every inner list passes through one
extra call), so the overhead grows with the number of wrapped items.

---

## 5. `text` Is Trusted Input

The only caller is `build_typing_rule`, which always passes a non-empty
`str` from `format_annotation`. The text is therefore not validated here.
"""
