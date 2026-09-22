# 📦 `rules/predicates/collections` — Container, Mapping & Iterable Rules

The `collections` package holds rules operating on containers, mappings, and iterables
as a whole — uniqueness across all items, membership of a single item or key, presence
of every key in a set, container type identity, and set-relationship checks (subset/
superset) against a reference collection.

```python
from ..base_class import Rule

class HasKey(Rule):
    ...
```

## A note on the shared `__contains__`/`__iter__` guard pattern

Every rule in this package that needs the value to support membership testing or
iteration checks for that capability explicitly (`hasattr(value, "__contains__")`,
`hasattr(value, "__iter__")`) before using it — rather than calling `in`/`iter()`
directly and catching whatever exception might result. This keeps `is_valid` a clean,
predictable `False` for any value that simply doesn't support the operation, instead of
risking an uncaught `TypeError` propagating out of what is supposed to be a pure
boolean check.

## A note on `is_container` as an internal building block

`IsContainer` exposes `is_container = IsContainer().is_valid` as a module-level
shortcut — the same pattern used throughout this library for parameterless rules.
`IsSubsetOf` and `IsSupersetOf` both reuse this shortcut internally to validate their
own `reference` constructor argument, rather than duplicating the container-type check.

---

## 🧭 Table of Contents

* [`AllUnique`](#allunique)
* [`HasItem`](#hasitem)
* [`HasKey`](#haskey)
* [`HasKeys`](#haskeys)
* [`IsContainer`](#iscontainer)
* [`IsSubsetOf`](#issubsetof)
* [`IsSupersetOf`](#issupersetof)

[⬅️ Back to main README](../../README.md#predicatescollections--containers-mappings--iterables)

---

### `AllUnique`

Every item in an iterable value must be unique — no duplicates anywhere in the
collection.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, AllUnique())
validate(value, all_unique)     # equivalent, via the pre-instantiated shortcut
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    if not hasattr(value, "__iter__"):
        return False

    items = list(value)
    try:
        return len(set(items)) == len(items)
    except TypeError:
        # Unhashable items fall back to an O(n²) manual comparison
        seen: list[Any] = []
        for item in items:
            if item in seen:
                return False
            seen.append(item)
        return True
```

The fast path uses a `set()` for `O(n)` uniqueness checking whenever every item is
hashable; unhashable items (lists, dicts, ...) fall back to a manual `O(n²)` comparison
rather than raising. On failure, the reported diagnostic explicitly lists every
duplicate value found, not just that duplicates exist.

[▲ Back to top](#-table-of-contents)

---

### `HasItem`

A container value must contain a single given item — the general-purpose counterpart
to `HasKey`, for containers where "membership" isn't specifically about mapping keys
(lists, sets, tuples, or any custom `__contains__` implementation).

**Parameters:**
* `item` (*Any*): The item that must be present.

**Example usage:**
```python
validate(value, HasItem("admin"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        hasattr(value, "__contains__")
        and self.item in value
    )
```

[▲ Back to top](#-table-of-contents)

---

### `HasKey`

A mapping value must contain a single given key.

**Parameters:**
* `key` (*Any*): The key that must be present.

**Example usage:**
```python
validate(value, HasKey("id"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        hasattr(value, "__contains__")
        and self.key in value
    )
```

On failure, a value that doesn't support membership at all is reported as a `TypeError`
("does not support key lookup"), while a mapping missing the key specifically is
reported as a `KeyError` naming that key — the same distinction Python's own `dict`
lookup semantics would draw.

[▲ Back to top](#-table-of-contents)

---

### `HasKeys`

A mapping value must contain **every** one of the given keys. Requires at least one key
at construction — calling it with none is rejected as a mistake, not silently treated
as "no constraint."

**Parameters:**
* `*keys` (*Any*): One or more keys, all of which must be present.

**Example usage:**
```python
validate(value, HasKeys("id", "name"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        hasattr(value, "__contains__")
        and all(key in value for key in self.keys)
    )
```

On failure, the reported diagnostic lists exactly which keys are missing, not just that
some are — computed by re-checking each key against the value when the exception is
built.

[▲ Back to top](#-table-of-contents)

---

### `IsContainer`

Value must be a non-string collection/container — a `list`, `tuple`, `set`,
`frozenset`, `dict`, or any custom type implementing the `Container` protocol. `str`
and `bytes` are explicitly excluded, even though both technically implement
`__contains__`, since neither represents a *collection of discrete elements* in the
sense this rule (and the rest of this package) cares about.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsContainer())
validate(value, is_container)     # equivalent, via the pre-instantiated shortcut
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    if isinstance(value, (str, bytes)):
        return False
    return isinstance(value, (list, tuple, set, frozenset, dict)) or isinstance(value, Container)
```

[▲ Back to top](#-table-of-contents)

---

### `IsSubsetOf`

Value, treated as a set, must be a subset of a given reference collection — every
element in the value must also appear in `reference`. The reference is validated as an
actual container at construction (via `is_container`) and precomputed into a `set` once,
for `O(1)` membership checks on every subsequent validation.

**Parameters:**
* `reference` (*Collection[Any]*): The collection every element of the value must
  belong to.

**Example usage:**
```python
validate(value, IsSubsetOf({"admin", "editor", "viewer"}))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    if not hasattr(value, "__iter__"):
        return False
    try:
        return set(value) <= self.reference
    except TypeError:
        return False
```

A value containing unhashable elements fails cleanly (`False`) rather than raising —
the same `except TypeError` guard applies both here and when the reported exception is
built, where it's distinguished as its own diagnostic ("contains unhashable elements
that cannot be compared as a set") from the ordinary "extra elements found" case. When
elements *are* comparable, the diagnostic lists the exact extra elements in
deterministic sorted order (via a shared `format_container` helper), avoiding
Python's own non-deterministic `set` repr ordering in error messages and test
assertions.

[▲ Back to top](#-table-of-contents)

---

### `IsSupersetOf`

Value, treated as a set, must be a superset of a given reference collection — every
element of `reference` must also appear in the value. The mirror image of
`IsSubsetOf`, sharing the same construction-time validation and precomputed `set`
strategy.

**Parameters:**
* `reference` (*Collection[Any]*): The collection every element of which must appear in
  the value.

**Example usage:**
```python
validate(value, IsSupersetOf({"read"}))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    if not hasattr(value, "__iter__"):
        return False
    try:
        return set(value) >= self.reference
    except TypeError:
        return False
```

Diagnostics mirror `IsSubsetOf`'s: unhashable elements are reported as their own
distinct failure, and an incomplete value's diagnostic lists exactly which required
elements from `reference` are missing, again in deterministic sorted order.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#predicatescollections--containers-mappings--iterables)