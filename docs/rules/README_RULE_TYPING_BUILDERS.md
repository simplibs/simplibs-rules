# 📦 `rules/typing/_builders` — Typing Annotation Decomposition Engine

The `_builders` package holds the actual construction logic behind `IsTyping`: one
function per *process* — a shared strategy for turning a particular shape of typing
annotation into a composed `Rule` tree — plus the `ORIGIN_TABLE` dispatch table that
routes any given annotation's `get_origin()` result to the builder that knows how to
handle it. This is the "LEGO" layer: rather than one branch per typing construct
(`list[T]`, `Iterable[T]`, `Sequence[T]`, `Set[T]`, ...), a handful of builders each
cover an entire *family* of structurally identical constructs.

```python
ORIGIN_TABLE = {
    list: build_elements_rule,
    dict: build_key_value_rule,
    typing.Union: build_any_of_rule,
    ...
}
```

## A note on the recursive, deferred `build_typing_rule` import

Every builder that needs to recursively decompose a *nested* annotation (an item type,
a key/value type, a Union member, ...) imports `build_typing_rule` from
`..build_typing_rule` **inside its own function body**, not at module load time.
`build_typing_rule` is what calls into `ORIGIN_TABLE` in the first place — a top-level
import here would create a circular import between the dispatcher and its own
builders. Deferring the import to the moment a builder actually runs breaks that
cycle at zero ongoing cost.

## A note on the table's shape

`ORIGIN_TABLE` deliberately maps *many* distinct `get_origin()` results onto the
*same* handful of builder functions — `list`, `set`, `frozenset`,
`collections.abc.Iterable/Sequence/Collection`, and their `typing.List`/`typing.Set`/
... legacy aliases all point at `build_elements_rule`. The table is what makes this
collapse possible: without it, each of those ~15 distinct origins would need its own
dispatch branch, even though the actual validation logic ("right container + rule per
item") is identical for every one of them.

---

## 🧭 Table of Contents

* [`ORIGIN_TABLE`](#origin_table)
* [`build_elements_rule`](#build_elements_rule)
* [`build_key_value_rule`](#build_key_value_rule)
* [`build_tuple_rule`](#build_tuple_rule)
* [`build_any_of_rule`](#build_any_of_rule)
* [`build_literal_rule`](#build_literal_rule)
* [`build_type_rule`](#build_type_rule)
* [`build_callable_rule`](#build_callable_rule)
* [`build_annotated_rule`](#build_annotated_rule)

[⬅️ Back to main README](../../README.md#typing--annotation-driven-validation)

---

### `ORIGIN_TABLE`

The dispatch table itself — a plain `dict` mapping every supported `get_origin()`
result to the builder function that processes it. Built once, at module import time;
no registration mechanism, no dynamic mutation.

```python
ORIGIN_TABLE = {
    # ELEMENTS — container + rule per item
    list: build_elements_rule,
    set: build_elements_rule,
    frozenset: build_elements_rule,
    collections_abc.Iterable: build_elements_rule,
    collections_abc.Sequence: build_elements_rule,
    collections_abc.Collection: build_elements_rule,
    typing.Iterable: build_elements_rule,
    typing.Sequence: build_elements_rule,
    typing.Collection: build_elements_rule,

    # TUPLE — routes internally between ELEMENTS and POSITIONAL
    tuple: build_tuple_rule,

    # KEY_VALUE — mapping + rule(key) + rule(value)
    dict: build_key_value_rule,
    collections_abc.Mapping: build_key_value_rule,
    collections_abc.MutableMapping: build_key_value_rule,
    typing.Mapping: build_key_value_rule,
    typing.MutableMapping: build_key_value_rule,

    # ANY_OF — Union[...] / X | Y
    typing.Union: build_any_of_rule,
    types.UnionType: build_any_of_rule,

    # LITERAL — Literal[...]
    typing.Literal: build_literal_rule,

    # TYPE — Type[T] / type[T]
    type: build_type_rule,
    typing.Type: build_type_rule,

    # CALLABLE — Callable[[...], R]
    collections_abc.Callable: build_callable_rule,
    typing.Callable: build_callable_rule,

    # ANNOTATED — Annotated[T, ...metadata...]
    typing.Annotated: build_annotated_rule,

    # Legacy typing aliases, for backward compatibility
    typing.List: build_elements_rule,
    typing.Set: build_elements_rule,
    typing.FrozenSet: build_elements_rule,
    typing.Tuple: build_tuple_rule,
    typing.Dict: build_key_value_rule,
}
```

Both the modern `collections.abc` spellings and the legacy `typing.List`/`typing.Dict`/
... aliases are registered side by side, pointing at the same builders — this is what
lets `build_typing_rule` handle annotations written in either style (or a mix)
identically, regardless of which Python version or code style produced them.

[▲ Back to top](#-table-of-contents)

---

### `build_elements_rule`

**ELEMENTS process.** Covers any generic where "is this the right container, and does
every item satisfy one shared item rule" fully describes the annotation — `list[T]`,
`set[T]`, `frozenset[T]`, `Iterable[T]`, `Sequence[T]`, `Collection[T]`, and
(via an explicit override, routed here by `build_tuple_rule`) homogeneous
`tuple[T, ...]`.

**Parameters:**
* `annotation` (*Any*): The full generic annotation, e.g. `list[int]`.
* `container_type` (*type | None*, keyword-only): Overrides the container type used
  for the base `IsInstance` check — needed specifically for `tuple[T, ...]`, where the
  real runtime container is `tuple`, but the caller (`build_tuple_rule`) already
  determined that before delegating here.

**Example usage:**
```python
build_typing_rule(list[int])
# -> AllOf(IsInstance(list), ForEach(IsInstance(int)))

build_typing_rule(list)
# -> IsInstance(list)   (bare generic — no item constraint)
```

**Under the hood:**
```python
def build_elements_rule(annotation: Any, *, container_type: type | None = None) -> Rule:
    origin = container_type or get_origin(annotation)
    parts: list[Rule] = [IsInstance(origin)]

    args = get_args(annotation)
    if args:
        item_rule = build_typing_rule(args[0])
        parts.append(ForEach(item_rule))

    return AllOf(*parts) if len(parts) > 1 else parts[0]
```

A bare, unsubscripted generic (`list` with no `[...]`) falls back to just the container
check — equivalent to `list[Any]`, since no item constraint was ever specified.

[▲ Back to top](#-table-of-contents)

---

### `build_key_value_rule`

**KEY_VALUE process.** Covers `dict[K, V]`, `Mapping[K, V]`, `MutableMapping[K, V]`,
and their `typing.*` aliases — a mapping type check plus one rule applied to every key
and one applied to every value.

**Parameters:**
* `annotation` (*Any*): The full generic annotation, e.g. `dict[str, int]`.

**Example usage:**
```python
build_typing_rule(dict[str, int])
# -> AllOf(
#      IsInstance(dict),
#      Compose(lambda m: m.keys(), ForEach(IsInstance(str))),
#      Compose(lambda m: m.values(), ForEach(IsInstance(int))),
#    )
```

**Under the hood:**
```python
def build_key_value_rule(annotation: Any) -> Rule:
    origin = get_origin(annotation)
    parts: list[Rule] = [IsInstance(origin)]

    args = get_args(annotation)
    if args:
        key_type, value_type = args
        key_rule = build_typing_rule(key_type)
        value_rule = build_typing_rule(value_type)

        parts.append(Compose(lambda mapping: mapping.keys(), ForEach(key_rule)))
        parts.append(Compose(lambda mapping: mapping.values(), ForEach(value_rule)))

    return AllOf(*parts) if len(parts) > 1 else parts[0]
```

`ForEach` alone validates a mapping's own iteration (its keys, by Python's `dict`
contract) — reaching a mapping's *values* needs an extraction step first, which is
exactly what `Compose(extractor, ForEach(...))` provides: `.keys()`/`.values()` as the
transformer, `ForEach(item_rule)` as the validator applied to that extracted view.

[▲ Back to top](#-table-of-contents)

---

### `build_tuple_rule`

**Router, not its own process.** `tuple[int, ...]` (homogeneous, unbounded length) and
`tuple[str, int, bool]` (heterogeneous, fixed length) share the same origin (`tuple`)
but need fundamentally different validation shapes — this function inspects
`get_args()` to decide which one applies, then delegates.

**Parameters:**
* `annotation` (*Any*): A tuple typing construct — bare `tuple`, `tuple[T, ...]`, or
  `tuple[A, B, C]`.

**Example usage:**
```python
build_typing_rule(tuple[int, ...])
# -> routes to build_elements_rule(..., container_type=tuple)
# -> AllOf(IsInstance(tuple), ForEach(IsInstance(int)))

build_typing_rule(tuple[str, int, bool])
# -> routes to the internal positional builder
# -> AllOf(IsInstance(tuple), HasLength(length=3), <index-0 rule>, <index-1 rule>, <index-2 rule>)
```

**Under the hood:**
```python
def build_tuple_rule(annotation: Any) -> Rule:
    args = get_args(annotation)

    if not args or _is_homogeneous_tuple_args(args):
        return build_elements_rule(annotation, container_type=tuple)

    return _build_positional_rule(annotation, args)


def _is_homogeneous_tuple_args(args: tuple[Any, ...]) -> bool:
    return len(args) == 2 and args[1] is Ellipsis
```

A bare, unsubscripted `tuple` (`args == ()`) is treated the same as the homogeneous
case — equivalent to "any tuple of any length/contents," routed to
`build_elements_rule` with no item constraint. The fixed-length branch
(`_build_positional_rule`) builds `IsInstance(tuple)`, an exact `HasLength` arity
check (so a wrong-length tuple fails with a clear diagnostic instead of an
`IndexError`), and one independent, recursively-built rule per position — each
checked via a small local closure comparing `value[index]` against that position's own
rule.

[▲ Back to top](#-table-of-contents)

---

### `build_any_of_rule`

**ANY_OF process.** Covers `Union[A, B, ...]` and `A | B` (`types.UnionType`) — both
map to this same function in `ORIGIN_TABLE`, since they represent the identical
concept spelled two different ways.

**Parameters:**
* `annotation` (*Any*): The full Union annotation, e.g. `int | str | None`.

**Example usage:**
```python
build_typing_rule(int | str | None)
# -> AnyOf(IsInstance(int), IsInstance(str), IsInstance(NoneType))
```

**Under the hood:**
```python
def build_any_of_rule(annotation: Any) -> Rule:
    members = get_args(annotation)
    return AnyOf(*(build_typing_rule(member) for member in members))
```

`Optional[T]` needs no special case at all — Python's own typing machinery resolves it
identically to `Union[T, None]`, and `NoneType` is an ordinary class, so it flows
through the same recursive `build_typing_rule` call as any other member, landing on a
plain `IsInstance(NoneType)`.

[▲ Back to top](#-table-of-contents)

---

### `build_literal_rule`

**LITERAL process.** Covers `Literal[1, 2, 3]`, `Literal["a", "b"]`, and mixed literal
sets — the one builder whose type arguments are concrete *values*, not nested
annotations, so no recursive `build_typing_rule` call is involved at all.

**Parameters:**
* `annotation` (*Any*): The full Literal annotation, e.g. `Literal["draft",
  "published"]`.

**Example usage:**
```python
build_typing_rule(Literal["draft", "published"])
# -> IsIn(("draft", "published"), strict=True)
```

**Under the hood:**
```python
def build_literal_rule(annotation: Any) -> Rule:
    allowed_values = get_args(annotation)
    return IsIn(allowed_values, strict=True)
```

Delegates straight to the existing `IsIn` rule, with `strict=True` — this is what
keeps `Literal[1]` from also accepting `True` (which `1 == True` would otherwise
allow), matching what a fully typing-faithful reading of `Literal` expects.

[▲ Back to top](#-table-of-contents)

---

### `build_type_rule`

**TYPE process.** Covers `Type[T]`/`type[T]` — a fundamentally different kind of
check than every other builder here: it asks whether the value **is itself a class**,
optionally a subclass of `T`, not whether an *instance* matches some shape.

**Parameters:**
* `annotation` (*Any*): The full annotation — `type[MyBase]`, `type[MyBase |
  OtherBase]`, `type[Any]`, or bare `type`.

**Example usage:**
```python
build_typing_rule(type[MyBase])
# -> AllOf(IsType(), IsSubclass(MyBase))

build_typing_rule(type[MyBase | OtherBase])
# -> AllOf(IsType(), AnyOf(IsSubclass(MyBase), IsSubclass(OtherBase)))

build_typing_rule(type[Any])
# -> IsType()   (Any base — unconstrained class object)
```

**Under the hood:**
```python
def build_type_rule(annotation: Any) -> Rule:
    parts: list[Rule] = [IsType()]

    args = get_args(annotation)
    if args:
        base = args[0]
        base_origin = get_origin(base)

        if base is Any:
            pass
        elif base_origin in (Union, types.UnionType):
            members = get_args(base)
            parts.append(AnyOf(*(IsSubclass(m) for m in members)))
        elif isinstance(base, type):
            parts.append(IsSubclass(base))
        else:
            raise_unsupported_annotation_error(annotation)

    return AllOf(*parts) if len(parts) > 1 else parts[0]
```

`type[Any]` is treated as equivalent to bare `type` — no subclass constraint added.
A Union base (`type[A | B]`) unpacks each member into its own `IsSubclass` check
combined with `AnyOf`, rather than recursing through `build_typing_rule` (which would
build `IsInstance` checks — wrong here, since the members describe acceptable *base
classes*, not acceptable instance types). Anything else as a base (e.g. a nested
generic) is rejected as unsupported rather than guessed at.

[▲ Back to top](#-table-of-contents)

---

### `build_callable_rule`

**CALLABLE process.** Covers `Callable[[int, str], bool]`, `Callable[..., R]`, and
bare `Callable` — all three collapse to the exact same runtime check.

**Parameters:**
* `annotation` (*Any*): The full Callable annotation. Its argument/return type
  information is intentionally never inspected.

**Example usage:**
```python
build_typing_rule(Callable[[int, str], bool])
# -> IsCallable()
```

**Under the hood:**
```python
def build_callable_rule(annotation: Any) -> Rule:
    return IsCallable()
```

Validating that a callable's *signature* actually matches the declared argument/return
types would require reconciling `inspect.signature()` against the annotation's own
argument list — a fundamentally harder problem than every other builder here solves,
and one static type checkers already own at check time. This builder validates the one
thing that's cheap and unambiguous to check at runtime: that the value is callable at
all.

[▲ Back to top](#-table-of-contents)

---

### `build_annotated_rule`

**ANNOTATED process.** Covers `Annotated[X, ...metadata...]` — the mechanism this
library's own rules use to attach themselves directly to an ordinary type hint (see
`Rule.annotated()` and `validated_type()`).

**Parameters:**
* `annotation` (*Any*): The full Annotated construct, e.g. `Annotated[int,
  greater_than(0)]`.

**Example usage:**
```python
build_typing_rule(Annotated[int, greater_than(0)])
# -> AllOf(IsInstance(int), GreaterThan(0))

build_typing_rule(Annotated[str, is_string & has_length(min_length=1)])
# -> AllOf(IsInstance(str), AllOf(IsInstance(str), HasLength(min_length=1)))
```

**Under the hood:**
```python
def build_annotated_rule(annotation: Any) -> Rule:
    underlying, *metadata = get_args(annotation)
    parts: list[Rule] = [build_typing_rule(underlying)]

    for item in metadata:
        if isinstance(item, Rule):
            parts.append(item)
        elif callable(item):
            parts.append(Compose(lambda value: value, item))

    return AllOf(*parts) if len(parts) > 1 else parts[0]
```

Every metadata item that is a `Rule` instance or a plain callable is folded into the
composed result via `AllOf`; anything else (a plain string, a framework-specific
object like a Pydantic `Field()`) is silently left alone — this library only claims
the metadata slots it recognizes, exactly as `Annotated`/PEP 593 was designed to allow
multiple, independent consumers to share the same annotation.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#typing--annotation-driven-validation)