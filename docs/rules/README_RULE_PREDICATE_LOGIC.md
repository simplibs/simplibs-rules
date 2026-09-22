# 📦 `rules/predicates/logic` — Identity, Membership & Custom Predicate Rules

The `logic` package holds two related families of rule plus one escape hatch: identity
comparisons (`Is`/`IsNot`, using Python's `is`, not `==`), membership checks against an
arbitrary collection (`IsIn`/`NotIn`), and `UserRule` — the bridge that lets any plain
callable predicate participate in this library's `Rule` ecosystem (composition,
diagnostics, `Annotated` metadata) without being formally written as a `Rule` subclass.

```python
from ..base_class import Rule

class IsIn(Rule):
    ...
```

## A note on `Is`/`IsNot` vs. `Equals`/`NotEquals`

`Is`/`IsNot` use `is`/`is not` (object identity), while `Equals`/`NotEquals`
(`comparisons/`) use `==`/`!=` (value equality). The distinction matters for the same
reason it matters in `checkers/`'s `IsTrue`/`IsFalse`: `0 == False` is `True` in Python,
but `0 is False` is not — so `Is(None)` and `Equals(None)` behave identically for
`None` specifically (since there is only ever one `None` object), but diverge for
mutable or numeric values where identity and equality can disagree.

## A note on `strict` in `IsIn`/`NotIn`

Both `IsIn` and `NotIn` accept an optional `strict: bool = False`. In non-strict mode,
membership uses Python's own `in` operator directly (`value in options`), which
compares by `==` — meaning `1 in (True, 2)` is `True`, since `1 == True`. `strict=True`
switches to an exact-type-plus-equality comparison (`type(opt) is type(value) and opt
== value`), rejecting that same `1` against `(True, 2)` because `int` and `bool` are
different types. This mirrors the same `bool`/`int` equality overlap this library
already documents elsewhere (e.g. the `Literal` builder in `rules/typing/`) — `strict`
exists specifically so a caller who needs to draw that distinction can.

---

## 🧭 Table of Contents

* [`Is`](#is)
* [`IsNot`](#isnot)
* [`IsIn`](#isin)
* [`NotIn`](#notin)
* [`UserRule`](#userrule)

[⬅️ Back to main README](../../README.md#predicateslogic--identity-membership--custom-predicates)

---

### `Is`

Value must be identical (`is`) to a specific object.

**Parameters:**
* `expected` (*Any*): The object to compare identity against.

**Example usage:**
```python
validate(value, Is(None))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return value is self.expected
```

[▲ Back to top](#-table-of-contents)

---

### `IsNot`

Value must **not** be identical (`is not`) to a specific object.

**Parameters:**
* `forbidden` (*Any*): The object the value must not be identical to.

**Example usage:**
```python
validate(value, IsNot(None))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return value is not self.forbidden
```

[▲ Back to top](#-table-of-contents)

---

### `IsIn`

Value must be a member of a given collection. Validates at construction that `options`
is an actual container.

**Parameters:**
* `options` (*Container[Any]*): The collection the value must belong to.
* `strict` (*bool*, default `False`): If `True`, requires both exact type match and
  equality against a member — see the note above.

**Example usage:**
```python
validate(value, IsIn(("draft", "published", "archived")))
validate(value, IsIn([1, 2], strict=True))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        if not self.strict:
            return value in self.options

        target_type = type(value)
        return any(
            type(opt) is target_type and opt == value
            for opt in self.options
        )
    except TypeError:
        return False
```

On failure, the diagnostic distinguishes "the value is comparable, but simply isn't one
of the options" from "the value can't even be looked up in this collection" (e.g. an
unhashable value against a `set`) — reported as `ValueError` and `TypeError`
respectively. The collection itself is rendered deterministically, and abbreviated to
just its type and size once its full representation grows past 60 characters, to keep
long option lists from producing unreadable error messages.

[▲ Back to top](#-table-of-contents)

---

### `NotIn`

Value must **not** be a member of a given collection — the mirror image of `IsIn`,
sharing the same `strict` semantics and construction-time container validation.

**Parameters:**
* `options` (*Container[Any]*): The collection the value must not belong to.
* `strict` (*bool*, default `False`): Same meaning as `IsIn`'s.

**Example usage:**
```python
validate(value, NotIn(("banned", "forbidden")))
validate(value, NotIn([0], strict=True))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        if not self.strict:
            return value not in self.options

        target_type = type(value)
        return all(
            type(opt) is not target_type or opt != value
            for opt in self.options
        )
    except TypeError:
        return True
```

Note the fallback direction is reversed from `IsIn`: an unhashable/incomparable value
can't possibly be *found* in the collection, so `NotIn` treats that as passing (`True`)
rather than failing — the logical mirror of `IsIn` treating the same situation as
failing. Diagnostics mirror `IsIn`'s formatting (deterministic, length-capped
collection rendering) for the "value unexpectedly found" case.

[▲ Back to top](#-table-of-contents)

---

### `UserRule`

Wraps an arbitrary user-supplied callable — a lambda, a named function, a bound method
— as a `Rule`. This is the escape hatch that lets a one-off predicate participate in
the same `|`/`&`/`~` composition, `Annotated` metadata, and diagnostic pipeline as
every purpose-built rule in this library, without needing to be written as a formal
`Rule` subclass.

**Parameters:**
* `rule` (*Callable[[Any], bool]*): The callable to wrap. Must be callable with exactly
  one positional argument and nothing else mandatory — checked at construction (see
  below).

**Example usage:**
```python
validate(value, UserRule(lambda v: v.startswith("user_")))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        return bool(self.rule(value))
    except Exception:
        return False
```

Any exception raised by the wrapped callable is caught and treated as a failed
validation, never propagated — preserving the same "`is_valid` never raises" contract
every rule in this library upholds, even for a callable this library did not write and
cannot vouch for.

**A note on the arity check:** at construction, `UserRule` inspects `rule`'s signature
(via `accepts_one_positional_argument`) to catch, ahead of time, a callable that
structurally cannot be called as `rule(value)` — for example `lambda: True` (accepts no
arguments at all) or a callable with a required keyword-only parameter. Without this
check, such a mistake would only surface the first time `is_valid` actually calls the
broken callable, and — because exceptions from `rule` are silently caught above — that
`TypeError` would be misread as "the value failed validation," when the real problem is
that the wrapped callable was never usable as a one-value predicate to begin with. The
check is deliberately permissive beyond that: callables requiring more than one
mandatory positional argument are still rejected, but extra *optional* parameters,
`*args`, and uninspectable callables (some C-implemented builtins) are all accepted, on
the principle that "can't tell" should never be treated the same as "definitely
broken."

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#predicateslogic--identity-membership--custom-predicates)