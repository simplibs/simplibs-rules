from typing import Any, get_args, get_origin

# Outers
from ....base_class import Rule
from ....containers import AllOf, Compose, ForEach
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

        # 3.1 Every key must satisfy key_rule — extracted via .keys() and checked via ForEach
        parts.append(Compose(lambda mapping: mapping.keys(), ForEach(key_rule)))

        # 3.2 Every value must satisfy value_rule — extracted via .values() and checked via ForEach
        parts.append(Compose(lambda mapping: mapping.values(), ForEach(value_rule)))

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

## 1. Composition via `Compose` and `ForEach`

Instead of raw closures, `Compose` extracts iterable views (`mapping.keys()` and
`mapping.values()`) and passes them to `ForEach(rule)`. This guarantees that
full `Rule` semantics, error reporting, and exception generation (`build_exception`)
are preserved for failing keys or values.

---

## 2. Unsubscripted Generic Fallback

Unsubscripted mappings (`dict`, `Mapping`) yield `args == ()`. Step 3 is skipped,
returning a single `IsInstance(mapping)` rule equivalent to `dict[Any, Any]`.
"""