# 📦 `rules/containers` — Composable Rule Containers

The `containers` package holds every rule that combines *other* rules rather than
checking a value directly — the connective tissue that turns individual predicates
(`IsInteger`, `HasLength`, `Regex`, ...) into arbitrarily complex validation trees. This
is also where every one of `Rule`'s own composition operators (`|`, `&`, `~`) actually
resolves to: `rule1 & rule2` is nothing more than `AllOf(rule1, rule2)` written with an
operator instead of a class name.

```python
from ..base_class import Rule

class AllOf(Rule):
    ...
```

## A note on mixed `Rule`/callable composition

Every container in this package accepts either a `Rule` instance or a plain callable
predicate anywhere it expects "a rule" — `AllOf(IsInteger(), lambda v: v > 0)` is just
as valid as `AllOf(IsInteger(), GreaterThan(0))`. Three small shared helpers make this
transparent everywhere in this package:

* **`as_predicate(rule)`** — returns `rule.is_valid` for a `Rule` instance, or `rule`
  itself for a plain callable, giving every container a single, uniform way to *call*
  either kind.
* **`build_child_exception(rule, value, value_name, context)`** — delegates to
  `rule.build_exception(...)` for a `Rule` instance, or falls back to the shared
  `build_validation_error(...)` factory for a plain callable, so every container can
  produce a proper diagnostic regardless of which kind of rule actually failed.
* **`describe_rule(rule, *, parenthesize=())`** — returns the rule's own `describe()` text
  for a `Rule` instance (the class name unless the rule overrides it), or
  `__name__`/`repr()` for a plain callable, for building readable messages and for
  composing the containers' own `describe()` text. `parenthesize` lists rule types
  that are wrapped in parentheses when they appear as an operand (see
  [Descriptions and precedence](#descriptions-and-precedence)). If a (user-written)
  `describe()` raises or returns anything but a non-empty `str`, the class name is used
  instead, so a faulty description never replaces the validation error it was meant to
  explain.

Every container documented below relies on these three helpers internally; they are not
part of this package's public surface.

## Descriptions and precedence

Every container implements [`Rule.describe()`](README_RULE_CLASS.md#describe) by composing
the descriptions of the rules it holds, so a tree of rules reads like the expression it
was built from, and failure cards name each alternative by what it requires instead of
by class name:

```python
(IsInstance(int) | IsNone()).describe()          # -> "int | None"
(IsInstance(int) & GreaterThan(0)).describe()    # -> "int & > 0"
(~IsNone()).describe()                           # -> "not None"
```

| Container  | `describe()` form             | Operand wrapped in parentheses                    |
|------------|-------------------------------|---------------------------------------------------|
| `AllOf`    | `a & b & c`                   | `AnyOf`, `Compose`                                |
| `AnyOf`    | `a \| b \| c`                 | `Compose`                                         |
| `NoneOf`   | `none of (a, b)`              | — (operands are comma-separated)                  |
| `Not`      | `not a`                       | `AllOf`, `AnyOf`, `Compose`                       |
| `ForEach`  | `each a`                      | `AllOf`, `AnyOf`, `Compose`                       |
| `Compose`  | `after f: v`                  | — (prefix form; embedding containers wrap it)     |
| `Described`| fixed text                    | —                                                 |

`&` binds tighter than `|`, so only an `AnyOf` needs parentheses inside an `AllOf`
(`(a | b) & c`), while an `AllOf` inside an `AnyOf` reads naturally (`a & b | c`).
`Compose` is always wrapped by the container that embeds it, because its prefix form
would otherwise read as covering everything to its right.

> The wrapping decision is made by rule *type*, because the text alone cannot reveal
> whether an operand is compound. A `Described` operand is never wrapped; its text is
> used as it is.

---

## 🧭 Table of Contents

* [`AllOf`](#allof)
* [`AnyOf`](#anyof)
* [`NoneOf`](#noneof)
* [`Not`](#not)
* [`ForEach`](#foreach)
* [`Compose`](#compose)
* [`Described`](#described)

[⬅️ Back to main README](../../README.md#containers--composing-other-rules)

---

### `AllOf`

Value must satisfy **every** one of the given rules — the container behind the `&`
operator. Rejects an unambiguous mistake at construction (calling it with zero rules),
and self-flattens any nested `AllOf` passed among its arguments, so that a chained
expression like `a & b & c` produces one flat `AllOf(a, b, c)` rather than a needlessly
nested `AllOf(AllOf(a, b), c)`.

**Parameters:**
* `*rules` (*Rule | Callable[[Any], bool]*): One or more rules or callables. At least
  one is required.

**Example usage:**
```python
validate(value, AllOf(IsInteger(), GreaterThan(0)))
validate(value, IsInteger() & GreaterThan(0))     # equivalent, via the & operator
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return all(
        as_predicate(rule)(value)
        for rule in self.rules
    )
```

**Description:** the operand texts joined with `&` — `"a & b & c"`, with an `AnyOf` or
`Compose` operand in parentheses.

On failure, `build_exception` delegates to whichever rule in `self.rules` failed
*first* — the returned diagnostic is that rule's own exception card, not a generic
"AllOf failed" message, so a failing `IsInteger() & GreaterThan(0)` reports exactly
which of the two conditions was actually violated.

[▲ Back to top](#-table-of-contents)

---

### `AnyOf`

Value must satisfy **at least one** of the given rules — the container behind the `|`
operator. Same construction-time guard (at least one rule required) and same
self-flattening behavior as `AllOf`, mirrored for `|`-chained expressions.

**Parameters:**
* `*rules` (*Rule | Callable[[Any], bool]*): One or more rules or callables. At least
  one is required.

**Example usage:**
```python
validate(value, AnyOf(IsInteger(), IsFloat()))
validate(value, IsInteger() | IsFloat())     # equivalent, via the | operator
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return any(
        as_predicate(rule)(value)
        for rule in self.rules
    )
```

**Description:** the operand texts joined with `|` — `"a | b | c"`, with a `Compose`
operand in parentheses.

Because no single rule is "the one that failed" when *all* of them fail together,
`build_exception` reports every member's description at once rather than pointing at
just one:

```text
Expected:  value satisfying at least one of: list[int], set[int], str
Problem:   Value did not satisfy any of: list[int], set[int], str.
```

[▲ Back to top](#-table-of-contents)

---

### `NoneOf`

Value must satisfy **none** of the given rules — the inverse of `AnyOf`. Useful for
forbidding a set of conditions together in one readable card, rather than negating each
one separately (`~IsZero() & ~IsNone()` vs. `NoneOf(IsZero(), IsNone())`).

**Parameters:**
* `*rules` (*Rule | Callable[[Any], bool]*): One or more rules or callables. At least
  one is required.

**Example usage:**
```python
validate(value, NoneOf(IsZero(), IsNone()))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return not any(as_predicate(rule)(value) for rule in self.rules)
```

**Description:** `"none of (a, b)"`.

`build_exception` names specifically *which* forbidden rule(s) the value unexpectedly
matched (not just that one of them did), by re-evaluating each rule against the value
when building the diagnostic — e.g. `"Value unexpectedly satisfied forbidden rule(s):
None."`

[▲ Back to top](#-table-of-contents)

---

### `Not`

Value must **not** satisfy the given single rule or predicate — the container behind
the `~` operator. Unlike `AllOf`/`AnyOf`/`NoneOf`, wraps exactly one rule, not a
variadic list.

**Parameters:**
* `rule` (*Rule | Callable[[Any], bool]*): The single rule or callable to negate.

**Example usage:**
```python
validate(value, Not(IsNone()))
validate(value, ~IsNone())     # equivalent, via the ~ operator
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return not as_predicate(self.rule)(value)
```

**Description:** `"not a"`, with an `AllOf`, `AnyOf` or `Compose` operand in
parentheses — `"not (a | b)"`.

[▲ Back to top](#-table-of-contents)

---

### `ForEach`

Every item in an **iterable** value must satisfy the given rule — the standard way to
validate the contents of a collection (`list`, `tuple`, `set`, a generator, ...) against
one shared item rule.

**Parameters:**
* `rule` (*Rule | Callable[[Any], bool]*): The rule every item must satisfy.

**Example usage:**
```python
validate([1, 2, 3], ForEach(IsInteger()))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        items = iter(value)
    except TypeError:
        return False

    predicate = as_predicate(self.rule)
    return all(predicate(item) for item in items)
```

**Description:** `"each a"`, with an `AllOf`, `AnyOf` or `Compose` operand in
parentheses — `"each (a | b)"`.

A value that isn't iterable at all simply fails (`is_valid` returns `False`) rather than
raising a `TypeError` outward. On failure, `build_exception` locates the *specific*
failing item by index and reports it with a positional label (`value_name[2]`, e.g.
`"ages[2]"`), rather than a generic "some item failed" message — and if the value wasn't
iterable in the first place, it delegates to `IsIterable`'s own diagnostic instead of
reporting a fabricated item failure.

[▲ Back to top](#-table-of-contents)

---

### `Compose`

Transforms the value first, then validates the *transformed* result — the tool for
"normalize, then check" patterns (trim whitespace before checking length, extract a
dict value before checking its type, ...) that a plain predicate rule can't express on
its own.

**Parameters:**
* `transformer` (*Callable[[Any], Any]*): A callable applied to the value before
  validation. Any exception it raises is treated as a failed transformation, not
  propagated.
* `validator` (*Rule | Callable[[Any], bool]*): The rule or callable applied to the
  *transformed* result.

**Example usage:**
```python
validate(value, Compose(str.strip, HasLength(min_length=1)))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        transformed = self.transformer(value)
    except Exception:
        return False

    return as_predicate(self.validator)(transformed)
```

**Description:** `"after f: v"` — the transformer's name followed by the validator's
description (`"after strip: length at least 1"`). The containers that embed a `Compose`
wrap it in parentheses.

`build_exception` distinguishes two different failure points and reports each with its
own diagnostic: a `transformer` that itself raises produces a
`COMPOSE_TRANSFORM_FAILED_ERROR` naming the exception it raised, while a `transformer`
that succeeds but whose result fails `validator` delegates to that validator's own
`build_exception` against the *transformed* value — so the reported diagnostic always
matches what actually went wrong, not just "Compose failed."

[▲ Back to top](#-table-of-contents)

---

### `Described`

Behaves **exactly like the wrapped rule**, but describes itself with a fixed text. It
exists for rule trees whose structure no longer reads like what the user wrote:
`list[int]` decomposes into `AllOf(IsInstance(list), ForEach(IsInstance(int)))`, which
would describe itself as `"list & each int"`. `build_typing_rule` wraps such trees with
the annotation's own spelling (`"list[int]"`), so a Union of them reads
`"list[int] | set[int] | str"`.

**Parameters:**
* `rule` (*Rule | Callable[[Any], bool]*): The rule or callable to wrap.
* `text` (*str*): The description to report. Trusted input — it is not validated.

**Example usage:**
```python
rule = Described(AllOf(IsInstance(list), ForEach(IsInstance(int))), "list[int]")

rule.is_valid([1, 2, 3])   # -> True
rule.describe()            # -> "list[int]"
```

**Under the hood:**
```python
def is_valid(self, value: Any) -> bool:
    return as_predicate(self.rule)(value)

def describe(self) -> str:
    return self.text

def build_exception(self, value, value_name=None, context=None) -> Exception:
    return build_child_exception(self.rule, value, value_name, context)
```

`build_exception` delegates to the wrapped rule, so the failure card still names the
exact failing sub-rule; only the summary text used by other containers changes.
A `Described` is never flattened by `AllOf`/`AnyOf` (only exact `AllOf`/`AnyOf`
instances are), so it stays one operand and keeps its text. It is a wrapper, not an
attribute on the rule, because a rule used directly as an annotation (or the shared
`IsAny` singleton) must never be mutated.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#containers--composing-other-rules)
