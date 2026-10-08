from typing import Any, Callable
# Outers
from ...base_class import Rule


def describe_rule(
    rule: Rule | Callable[[Any], bool],
    *,
    parenthesize: tuple[type, ...] = (),
) -> str:
    """Return a readable description of a rule or function, for use in error messages.

    Args:
        rule: A Rule instance (it describes itself via `describe()`) or a
            plain callable (described by its `__name__`).
        parenthesize: Rule types that must be wrapped in parentheses when
            they appear as an operand of an operator-like description, e.g.
            an `AnyOf` inside an `AllOf`: "(a | b) & c".

    Returns:
        The description text, wrapped in parentheses if `rule` is an
        instance of one of the `parenthesize` types.
    """

    # 1. Handling for a formal Rule instance — the rule describes itself
    if isinstance(rule, Rule):

        # 1.1 A faulty describe() must never mask the error being reported
        # noinspection PyBroadException
        try:
            text = rule.describe()
        except Exception:
            text = None
        if not isinstance(text, str) or not text:
            text = type(rule).__name__

        # 1.2 Wrap compound operands so operator precedence stays unambiguous
        if parenthesize and isinstance(rule, parenthesize):
            return f"({text})"
        return text

    # 2. Handling for a user-defined rule
    return getattr(rule, "__name__", repr(rule))


_DESIGN_NOTES = """
# describe_rule — Rule Representation Extraction Helper

## Purpose
Provides a standardized, concise string representation for validation rules
and callables to be embedded in composite error messages and in the
`describe()` text of container rules.

---

## 1. Execution Rationale

* **Rule Instance Branching:**
  A formal `Rule` describes itself through `Rule.describe()`. The default is
  the class name; rules with parameters or structure override it
  (`"> 0"`, `"int | None"`).
* **Callable Fallback:**
  Safely extracts `__name__` or falls back to `repr(rule)` for raw
  functions, lambdas and callable objects.

---

## 2. Why Description Lives on the Rule, Not Here

An earlier version returned `type(rule).__name__` for every rule and argued
that a `__name__` attribute on `Rule` would not pay off. That conclusion
was about speed. The real problem is information: the class name cannot
carry parameters or structure, so `AllOf(IsInstance(list), ForEach(...))`
and `AllOf(IsInteger(), GreaterThan(0))` both read "AllOf". A method
(`describe()`) lets every rule say what it requires, and containers compose
the text of their children recursively.

---

## 3. Defensive Boundary

This helper is the single place that calls `Rule.describe()` while building
diagnostics. If a (user-written) `describe()` raises or returns something
that is not a non-empty `str`, the class name is used instead — a faulty
description must never replace the validation error it was meant to explain.

---

## 4. `parenthesize` Keeps Precedence Readable

Containers pass the rule types that bind looser than their own operator.
`AllOf` passes `AnyOf` (and `Compose`), so `a & (b | c)` is never printed
as the ambiguous "a & b | c". The decision is made by rule *type* because
the text alone cannot reveal whether it is compound.

* **Only Rule Instances Are Wrapped:**
  A plain callable is described by its name, which is never compound, so
  `parenthesize` does not apply to it.
* **Fallback Is Wrapped Too:**
  If a faulty `describe()` forces the class-name fallback, the name is still
  wrapped when the rule's type is listed, so the structure stays readable.
"""
