from .as_predicate import as_predicate
from .build_child_exception import build_child_exception
from .describe_rule import describe_rule
from .format_key_label import format_key_label
from .format_value_label import format_value_label
from .shorten_repr import shorten_repr


_DESIGN_NOTES = """
# Container Rules Internal Helpers Sub-Package

## Purpose
Shared runtime helpers used internally by container rules (`AllOf`, `AnyOf`,
`NoneOf`, `Not`, `ForEach`, `ForEachKey`, `ForEachValue`, `Compose`) to
normalize child rules into predicates, delegate exception construction,
produce readable rule descriptions for diagnostic messages, and name the
failing entry of a mapping.

## Internal Components Registry

| Component               | Type     | Description                                                                     |
| :----------------------- | :------- | :--------------------------------------------------------------------------------|
| `as_predicate`            | Function | Normalizes a `Rule` instance or callable into a plain `Callable[[Any], bool]`.  |
| `build_child_exception`   | Function | Delegates exception construction to a child `Rule` or a callable fallback.      |
| `describe_rule`           | Function | Returns a readable description of a rule (`Rule.describe()`) or callable, optionally parenthesized. |
| `format_key_label`        | Function | Builds the label of a failing mapping key (`opts[key 'zz']`).                   |
| `format_value_label`      | Function | Builds the label of a failing mapping value, named by its key (`opts['b']`).    |
| `shorten_repr`            | Function | Returns `repr(value)` cut to a fixed length, so a long key cannot swamp a label. |
"""
