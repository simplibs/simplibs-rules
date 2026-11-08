from typing import Any
# Inners
from .shorten_repr import shorten_repr


def format_key_label(key: Any, value_name: str | None = None) -> str:
    """Build the label of a mapping key: `opts[key 'zz']`, or `[key 'zz']` without a name.

    Args:
        key: The failing key.
        value_name: The name of the validated mapping, if any.

    Returns:
        The label, marked as a key so it cannot be taken for a value.
    """

    # 1. The key marked as a key, shortened when it is long
    item = f"[key {shorten_repr(key)}]"

    # 2. Attach it to the name, if there is one
    return f"{value_name}{item}" if value_name else item


_DESIGN_NOTES = """
# format_key_label — Label of a Key

## Purpose
A key cannot be "indexed", so it needs a form of its own, and one that cannot be
confused with the label of a value: `opts[key 'zz']` versus `opts['zz']`.

## Form
Mirrors `format_value_label` (a bracket after the name) with the word `key`
inside. Without a name only the bracket part remains: `[key 'zz']`.

## Nesting
Because the bracket closes the label, a rule inside a composite key can append
its own part: `opts[key (1, 'x')][1]` reads naturally — the second part of the
key `(1, 'x')`.

## Single Place
The form of the label lives here and nowhere else.
"""
