from typing import Any
# Inners
from .shorten_repr import shorten_repr


def format_value_label(key: Any, value_name: str | None = None) -> str:
    """Build the label of a mapping value: `opts['b']`, or `['b']` without a name.

    Args:
        key: The key under which the failing value is stored.
        value_name: The name of the validated mapping, if any.

    Returns:
        The label, spelled like the access to the value in Python.
    """

    # 1. The key as it is written in Python code, shortened when it is long
    item = f"[{shorten_repr(key)}]"

    # 2. Attach it to the name, if there is one
    return f"{value_name}{item}" if value_name else item


_DESIGN_NOTES = """
# format_value_label — Label of a Value, Named by Its Key

## Purpose
`opts['b']` tells the user exactly which entry failed, where an index
(`opts[1]`) only tells the position in the iteration order.

## Form
The same spelling as the access in Python, so it can be read straight into the
code: `opts['b']`, `opts[2]`, `opts[('x', 1)]`. Without a name only the bracket
part remains: `['b']`.

## Nesting
The label is a plain prefix, so a rule inside the value keeps building on it:
`opts['a'][1]` for the second item of a list stored under `'a'`.

## Single Place
The form of the label lives here and nowhere else; changing it later means
editing this one file.
"""
