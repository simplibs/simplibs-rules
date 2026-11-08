from typing import Any, get_args, get_origin
# Outers
from ....base_class import Rule
from ....containers import AllOf, ForEachKey, ForEachValue
from ....predicates.introspection import IsInstance


def build_key_value_rule(annotation: Any) -> Rule:
    """KEY_VALUE process: mapping type check + rule(key) + rule(value).

    Covers dict[K, V], Mapping[K, V], MutableMapping[K, V], and any other
    mapping-shaped generic registered against this builder in the origin table.
    """
    # 1. Recursive build_typing_rule import — deferred to prevent cycles
    from ..build_typing_rule import build_typing_rule

    # 2. Base mapping check
    origin = get_origin(annotation)
    parts: list[Rule] = [IsInstance(origin)]

    # 3. Key/value rules, if the annotation specifies them
    args = get_args(annotation)
    if args:
        key_type, value_type = args
        key_rule = build_typing_rule(key_type)
        value_rule = build_typing_rule(value_type)

        # 3.1 Every key must satisfy key_rule — a failing key is labelled opts[key 'zz']
        parts.append(ForEachKey(key_rule))

        # 3.2 Every value must satisfy value_rule — a failing value is labelled opts['b']
        parts.append(ForEachValue(value_rule))

    # 4. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# key_value_builder — KEY_VALUE Process

## Purpose
Handles mapping types (`dict[K, V]`, `Mapping[K, V]`, etc.) by combining a type
check with element-wise rules for keys and values.

---

## 1. Composition via `ForEachKey` and `ForEachValue`

The mapping itself is handed to `ForEachKey(rule)` and `ForEachValue(rule)`, so
the key stays available when an exception is built. A failing value is labelled
by its key (`opts['b']`), a failing key is marked as such (`opts[key 'zz']`).
Full `Rule` semantics, error reporting, and exception generation
(`build_exception`) are preserved for failing keys or values.

The earlier composition, `Compose(mapping.values(), ForEach(rule))`, passed a bare
view to `ForEach`, which could only report the position of the item
(`opts[1]`) — and could not tell a failing key from a failing value.

---

## 2. Check Order

`AllOf` checks the mapping type first, then the keys, then the values, so a
wrong key is reported before a wrong value.

---

## 3. Unsubscripted Generic Fallback

Unsubscripted mappings (`dict`, `Mapping`) yield `args == ()`. Step 3 is skipped,
returning a single `IsInstance(mapping)` rule equivalent to `dict[Any, Any]`.
"""
