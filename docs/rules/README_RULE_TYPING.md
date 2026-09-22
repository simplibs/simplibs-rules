# 📦 `rules/typing` — Annotation-Driven Validation

The `typing` package is the single largest, most structurally different rule in this
library: `IsTyping` doesn't check a value against one fixed condition — it takes an
arbitrary Python type annotation (`list[int]`, `dict[str, int] | None`,
`Literal["draft", "published"]`, a plain class, or even one of this library's own
`Rule` instances) and recursively *decomposes* it into an equivalent composed `Rule`
tree, built once at construction and then evaluated like any other rule.

```python
validate(value, IsTyping(list[int]))
validate(value, IsTyping(dict[str, int] | None))
validate(value, IsTyping(Literal["draft", "published"]))
```

## Why this rule exists

Every other rule in this library represents one fixed validation concept —
`IsInteger`, `HasLength`, `Regex`. `IsTyping` exists for a different, complementary
reason: Python code is already full of type annotations (function signatures,
dataclass fields, variable hints), and re-expressing every one of them by hand as a
composed `Rule` (`list[int]` → `AllOf(IsInstance(list), ForEach(IsInstance(int)))`)
would be tedious and error-prone to keep in sync. `IsTyping` reads the annotation
Python already has and builds the equivalent `Rule` tree automatically — this is also
exactly what powers `validate_call` and `validate_dataclass`, which apply `IsTyping`'s
own decomposition across an entire function signature or dataclass at once, without
needing any separate logic of their own for "what does this annotation mean."

## Why this package has more moving parts than any other rule

Every other rule in this library is a single, self-contained class. `IsTyping` can't
be, because the *thing it validates against* — a typing annotation — isn't one shape.
`list[int]`, `dict[str, int]`, `int | str`, `Literal[1, 2]`, and `Callable[[int], bool]`
are all completely different constructs requiring completely different logic to
interpret, and any one of them can be nested arbitrarily deep inside another
(`list[dict[str, int | None]]`). Rather than one enormous `if/elif` chain trying to
recognize every possible shape inline, this responsibility is split into three
cooperating layers:

1. **`build_typing_rule`** — the single recursive entry point. Given any annotation, it
   decides which of five paths applies (`Any`, a direct `Rule` instance, a plain class,
   a `NewType`, or a generic with an origin) and either returns a rule directly or
   hands off to layer 2.
2. **`ORIGIN_TABLE` + the builders** (`rules/typing/_builders/` — see its own
   documentation) — a dispatch table mapping each distinct `get_origin()` result to
   the one *process* (ELEMENTS, KEY_VALUE, ANY_OF, LITERAL, TYPE, CALLABLE, ANNOTATED,
   or the tuple router) that knows how to build a `Rule` for that shape. Every builder
   that needs to handle a *nested* annotation calls back into `build_typing_rule` —
   this is the recursion that lets `list[dict[str, int]]` resolve correctly without
   this package needing any concept of "how deep can this go."
3. **`IsTyping`** itself — a thin `Rule` wrapper around the whole mechanism, so the
   result of all that decomposition can be used exactly like any other rule
   (`.validate()`, `|`/`&`/`~` composition, `Annotated` metadata, ...).

`IsAny` and the `tools/` introspection helpers round out the package: the former is a
small structural building block the decomposition needs internally, the latter are
read-only utilities for asking *what* this mechanism supports, without needing to
actually validate a value.

---

## 🧭 Table of Contents

* [`build_typing_rule`](#build_typing_rule)
* [`IsTyping`](#istyping)
* [`IsAny`](#isany)
* [`is_supported_annotation`](#is_supported_annotation)
* [`get_supported_origins`](#get_supported_origins)

[⬅️ Back to main README](../../README.md#typing--annotation-driven-validation)

---

### `build_typing_rule`

The recursive dispatcher every annotation — top-level or nested — passes through
exactly once per recursion level. Not a `Rule` itself; a plain function returning one.
`IsTyping.__init__` calls it exactly once; every builder in `_builders/` that needs to
handle a nested annotation slot calls it again from inside its own function body. See
[`rules/typing/_builders`](../_builders/README.md) for the full builder-by-builder
reference this dispatches into.

**Parameters:**
* `annotation` (*Any*): A plain class, a `Rule` instance, `typing.Any`, a `NewType`, or
  any supported typing construct — `Annotated`, `Union`/`|`, `Literal`, `Type`,
  `Callable`, or a `list`/`set`/`dict`/`tuple`/`Iterable`/`Sequence`/`Mapping`/...
  generic (see `get_supported_origins()` for the exhaustive list of recognized
  origins).

**Returns:**
* `Rule`: A single, fully composed `Rule` instance equivalent to the given annotation.

**Raises:**
* `ParamError`: If the annotation (or any nested fragment of it, at any recursion
  depth) is not a recognized type or typing construct.

**Example usage:**
```python
build_typing_rule(int)                         # -> IsInstance(int)
build_typing_rule(list[int])                   # -> AllOf(IsInstance(list), ForEach(IsInstance(int)))
build_typing_rule(is_integer & greater_than(0)) # -> the Rule instance itself, unchanged
```

**Under the hood:**
```python
def build_typing_rule(annotation: Any) -> Rule:
    # 1. Any — unconstrained, checked first since it has no origin
    if annotation is Any:
        return _IS_ANY

    origin = get_origin(annotation)

    # 2. No origin — a direct Rule, a plain class, a NewType, or unsupported
    if origin is None:
        if isinstance(annotation, Rule):
            return annotation
        if isinstance(annotation, type):
            return IsInstance(annotation)
        if hasattr(annotation, "__supertype__"):
            return build_typing_rule(annotation.__supertype__)
        raise_unsupported_annotation_error(annotation)

    # 3. Origin present — look up the process that handles it
    builder = ORIGIN_TABLE.get(origin)
    if builder is None:
        raise_unsupported_annotation_error(annotation)

    return builder(annotation)
```

**A note on why the order of checks matters.** Each branch above must run before the
ones after it, or it silently never triggers: `Any` has no origin and isn't a `type`
instance, so it must be caught before the "no origin" branch would otherwise reject it;
a `Rule` instance is checked before `isinstance(annotation, type)` since a `Rule`
instance is never itself a class; `NewType` unwrapping (`hasattr(annotation,
"__supertype__")`) must come before the final "unsupported" fallback, or every
`NewType` would be rejected outright instead of resolved to its underlying type.

**A note on a `Rule` instance used directly as an annotation.** This is what lets `x:
is_integer` work identically to `x: int` when passed through `validate_call` or any
other consumer of `build_typing_rule` — the `Rule` is recognized and returned as-is,
with no further decomposition needed, since it's already exactly what this function
would otherwise be trying to produce.

[▲ Back to top](#-table-of-contents)

---

### `IsTyping`

The public-facing `Rule` wrapper around the whole decomposition mechanism. Everything
about *interpreting* the annotation happens once, in `__init__`, via
`build_typing_rule`; `is_valid` and `build_exception` are pure delegation to the
resulting composed rule.

**Parameters:**
* `annotation` (*Any*): Anything `build_typing_rule` accepts.

**Example usage:**
```python
validate(value, IsTyping(list[int]))
validate(value, IsTyping(dict[str, int] | None))
validate(value, IsTyping(Literal["draft", "published"]))
```

**Under the hood:**
```python
def __init__(self, annotation: Any) -> None:
    self.annotation = annotation
    self.rule = build_typing_rule(annotation)

def is_valid(self, value: Any) -> bool:
    return self.rule.is_valid(value)

def build_exception(self, value, value_name=None, context=None):
    return self.rule.build_exception(value, value_name=value_name, context=context)
```

Because decomposition happens once at construction — not on every `is_valid()` call —
reusing the same `IsTyping` instance across many validations (in a loop, or as a
building block inside another composed rule) never re-walks the annotation.
`build_exception` delegates to the already-built rule's own diagnostic, which is
always at least as specific as anything this class could construct generically — the
same "delegate to whichever part actually failed" pattern `AllOf`/`AnyOf` use for
their own children.

[▲ Back to top](#-table-of-contents)

---

### `IsAny`

The structural counterpart to `typing.Any` — not a rule you'd reach for directly, but
the concrete `Rule` `build_typing_rule` plugs in wherever an annotation slot resolves
to `Any` (a bare `Any` annotation, or `Any` appearing nested — `list[Any]`, `dict[str,
Any]`). Every annotation slot must produce *some* `Rule` for the composed tree to stay
uniform; `IsAny` is what lets "this slot accepts anything" be expressed the same way as
every other slot, rather than needing a special "skip this slot" case throughout the
builders.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsAny())          # always passes — rarely written by hand
build_typing_rule(list[Any])      # -> AllOf(IsInstance(list), ForEach(IsAny()))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return True
```

`is_valid` unconditionally returns `True` rather than performing a technically-always-
true check like `isinstance(value, object)` — every value in Python is an instance of
`object`, so the two are behaviorally identical, but `return True` honestly states what
`Any` actually means (no constraint at all) instead of implying a real check is
happening. `build_exception` exists only to satisfy `Rule`'s abstract contract and is
never reachable in practice, since `is_valid` can never return `False`.

[▲ Back to top](#-table-of-contents)

---

### `is_supported_annotation`

A read-only introspection helper: asks "could `IsTyping`/`build_typing_rule` handle
this annotation?" without needing a value to validate against — useful for checking an
annotation's shape ahead of time (e.g. before applying `validate_call` to a function,
or when building tooling around this library).

**Parameters:**
* `annotation` (*Any*): Any type annotation, class, or typing construct to inspect.

**Returns:**
* `bool`: `True` if the annotation (including every nested fragment of it) can be
  successfully compiled into a `Rule`; `False` if any part of it is unsupported.

**Example usage:**
```python
is_supported_annotation(list[int])          # -> True
is_supported_annotation(dict[str, MyClass]) # -> True
is_supported_annotation(SomeUnknownGeneric[int])  # -> False
```

**Under the hood:**
```python
def is_supported_annotation(annotation: Any) -> bool:
    try:
        build_typing_rule(annotation)
        return True
    except ParamError:
        return False
```

This is a genuine attempt at full decomposition, not a shallow origin lookup —
`build_typing_rule`'s own recursion means a *nested* unsupported fragment (e.g.
`list[SomeUnknownGeneric[int]]`) is caught too, not just a top-level one.

[▲ Back to top](#-table-of-contents)

---

### `get_supported_origins`

A read-only introspection helper exposing exactly which `get_origin()` results
`ORIGIN_TABLE` currently recognizes — the complete, authoritative list of supported
generic origins, straight from the table itself rather than a separately maintained
list that could drift out of sync.

**Parameters:**
* *(none)*

**Returns:**
* `frozenset[Any]`: Every key currently registered in `ORIGIN_TABLE` — standard
  built-in origins (`list`, `dict`, `tuple`, ...), `collections.abc` and `typing`
  variants, and special constructs (`Union`, `Literal`, `Callable`, `Type`,
  `Annotated`).

**Example usage:**
```python
get_supported_origins()
# -> frozenset({list, set, frozenset, dict, tuple, typing.Union, typing.Literal, ...})
```

**Under the hood:**
```python
def get_supported_origins() -> frozenset[Any]:
    return frozenset(ORIGIN_TABLE.keys())
```

Returned as an immutable `frozenset` rather than the table's own `dict` (or a plain
`set`) — deliberately preventing accidental mutation of what is meant to be read-only,
descriptive information about this package's own supported surface.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#typing--annotation-driven-validation)