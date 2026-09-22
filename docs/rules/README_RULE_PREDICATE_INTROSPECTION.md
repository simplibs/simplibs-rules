# 📦 `rules/predicates/introspection` — Structural & Reflective Rules

The `introspection` package holds rules that inspect a value's *shape* rather than its
specific content — whether it has a given attribute, supports `len()`, is callable,
hashable, iterable, a dataclass, an instance of specific types, or a type/class object
itself. These rules answer "what kind of thing is this" rather than "does this thing
satisfy a specific value constraint."

```python
from ..base_class import Rule

class IsInstance(Rule):
    ...
```

## A note on the `hasattr`/`callable`/`iter()`/`hash()` guard pattern

Several rules in this package (`IsCallable`, `IsHashable`, `IsIterable`) are thin,
direct wrappers around a single built-in Python capability check — `callable(value)`,
`hash(value)`, `iter(value)`. Where the underlying built-in can raise rather than
return a boolean (`hash()` and `iter()` both raise `TypeError` on unsupported input),
`is_valid` catches that and reports `False` instead of letting it propagate — the same
"never raise from `is_valid`" contract every rule in this library upholds.

---

## 🧭 Table of Contents

* [`IsInstance`](#isinstance)
* [`IsType`](#istype)
* [`IsSubclass`](#issubclass)
* [`IsDataclass`](#isdataclass)
* [`IsCallable`](#iscallable)
* [`IsHashable`](#ishashable)
* [`IsIterable`](#isiterable)
* [`HasAttribute`](#hasattribute)
* [`HasLength`](#haslength)

[⬅️ Back to main README](../../README.md#predicatesintrospection--structural--reflective-checks)

---

### `IsInstance`

Value must be an instance of one or more given types — the direct rule form of
Python's own `isinstance()`. Requires at least one type at construction, and validates
that every argument given actually *is* a type (not, say, an instance mistakenly
passed in its place).

**Parameters:**
* `*types` (*type*): One or more types to check against.

**Example usage:**
```python
validate(value, IsInstance(int))
validate(value, IsInstance(int, float))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return isinstance(value, self.types)
```

[▲ Back to top](#-table-of-contents)

---

### `IsType`

Value must itself **be** a type — a class object, not an instance of one. The
foundation `IsSubclass` builds on for its own "is this even a class" guard.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsType())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return isinstance(value, type)
```

[▲ Back to top](#-table-of-contents)

---

### `IsSubclass`

Value must be a class that is a subclass of one or more given base types. Distinct
from `IsInstance` in exactly the way `issubclass()` differs from `isinstance()` — this
rule is about the class *itself*, not about instances of it.

**Parameters:**
* `*types` (*type*): One or more base types to check inheritance against.

**Example usage:**
```python
validate(bool, IsSubclass(int))
validate(MyClass, IsSubclass(BaseClass1, BaseClass2))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, type)
        and issubclass(value, self.types)
    )
```

On failure, the reported diagnostic distinguishes two different mistakes: passing an
*instance* where a class was expected ("is an instance of 'X', not a class object"),
versus passing a genuine class that simply doesn't inherit from the required base(s).

[▲ Back to top](#-table-of-contents)

---

### `IsDataclass`

Value must be a dataclass — either an instance of one, or the dataclass type itself.
A thin wrapper around `dataclasses.is_dataclass`, which already accepts both forms.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsDataclass())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return dataclasses.is_dataclass(value)
```

[▲ Back to top](#-table-of-contents)

---

### `IsCallable`

Value must be callable — a function, method, lambda, class, or any object implementing
`__call__`.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsCallable())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return callable(value)
```

[▲ Back to top](#-table-of-contents)

---

### `IsHashable`

Value must be hashable — usable as a `dict` key or a `set` member. A thin wrapper
around Python's own `hash()`, which raises `TypeError` on unhashable input (`list`,
`dict`, `set`) rather than returning a boolean.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsHashable())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        hash(value)
        return True
    except TypeError:
        return False
```

[▲ Back to top](#-table-of-contents)

---

### `IsIterable`

Value must be iterable — usable in a `for` loop, or with functions like `list()`,
`sum()`, or `sorted()`. A thin wrapper around Python's own `iter()`.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsIterable())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        iter(value)
        return True
    except TypeError:
        return False
```

[▲ Back to top](#-table-of-contents)

---

### `HasAttribute`

Value must have a given attribute — a thin wrapper around Python's own `hasattr()`.
Validates at construction that `attr_name` is actually a string.

**Parameters:**
* `attr_name` (*str*): The attribute name to check for.

**Example usage:**
```python
validate(value, HasAttribute("append"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return hasattr(value, self.attr_name)
```

[▲ Back to top](#-table-of-contents)

---

### `HasLength`

Value's length (via `len()`) must equal an exact `length`, or fall within an
inclusive `[min_length, max_length]` range — two mutually exclusive modes, chosen by
which arguments are given. Requires at least one of `length`/`min_length`/`max_length`;
combining `length` with either boundary is rejected as a conflicting request, and an
inverted range (`min_length > max_length`) is rejected too — all checked at
construction, not deferred to validation time.

**Parameters:**
* `length` (*int | None*): Exact required length. Mutually exclusive with
  `min_length`/`max_length`.
* `min_length` (*int | None*, keyword-only): Minimum allowed length.
* `max_length` (*int | None*, keyword-only): Maximum allowed length.

**Example usage:**
```python
validate(value, HasLength(length=10))
validate(value, HasLength(min_length=1))
validate(value, HasLength(max_length=10))
validate(value, HasLength(min_length=1, max_length=10))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        length = len(value)
    except TypeError:
        return False

    if self.length is not None:
        return length == self.length

    if self.min_length is not None and length < self.min_length:
        return False
    if self.max_length is not None and length > self.max_length:
        return False

    return True
```

On failure, the diagnostic distinguishes "this value has no `len()` at all" from "this
value has a length, but not the expected one" — and in the latter case, states the
actual length found alongside a plain-language description of what was expected
(`"length 10"`, `"length between 1 and 10"`, `"length at least 1"`, `"length at most
10"`), built from whichever of the three constructor arguments was actually given.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#predicatesintrospection--structural--reflective-checks)