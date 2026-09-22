# 📦 `rules/predicates/checkers` — Basic State & Identity Checks

The `checkers` package holds the simplest possible category of rule in the entire
library: direct identity comparisons (`is None`, `is True`, `is False`) and
emptiness checks via `len()`. None of these rules take any constructor parameters —
each one represents exactly one fixed, unconfigurable condition, which is also why
every one of them is exposed as a ready-to-use, pre-instantiated shortcut
(`is_none`, `is_true`, `is_false`, `is_empty`, `not_empty`) rather than needing to be
constructed by hand at every use site.

```python
from ..base_class import Rule

class IsNone(Rule):
    ...
```

## A note on `is`, not `==`

`IsNone`, `IsTrue`, and `IsFalse` all use Python's `is` operator, not `==`. This is
deliberate and matters in practice: `0 == False` and `1 == True` are both `True` in
Python, so an equality-based check would incorrectly accept `0` where `IsFalse()` is
meant to strictly mean "the literal boolean `False`, nothing else." Using `is` makes
these three rules exact identity checks, immune to that kind of accidental type
coercion.

---

## 🧭 Table of Contents

* [`IsNone`](#isnone)
* [`IsTrue`](#istrue)
* [`IsFalse`](#isfalse)
* [`IsEmpty`](#isempty)
* [`NotEmpty`](#notempty)

[⬅️ Back to main README](../../README.md#predicatescheckers--basic-state--identity)

---

### `IsNone`

Value must be `None`, checked via identity (`is`).

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsNone())
validate(value, is_none)     # equivalent, via the pre-instantiated shortcut
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return value is None
```

[▲ Back to top](#-table-of-contents)

---

### `IsTrue`

Value must be the literal boolean `True` — not merely truthy. `1`, `"yes"`, and `[0]`
are all truthy in Python but all fail this rule; only `True` itself passes.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsTrue())
validate(value, is_true)     # equivalent, via the pre-instantiated shortcut
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return value is True
```

[▲ Back to top](#-table-of-contents)

---

### `IsFalse`

Value must be the literal boolean `False` — not merely falsy. `0`, `""`, and `[]` are
all falsy in Python but all fail this rule; only `False` itself passes.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsFalse())
validate(value, is_false)     # equivalent, via the pre-instantiated shortcut
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return value is False
```

[▲ Back to top](#-table-of-contents)

---

### `IsEmpty`

Value must be empty, as reported by `len()` — `0`, `[]`, `""`, `{}`, and `set()` all
pass; a value that doesn't support `len()` at all simply fails, rather than raising.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsEmpty())
validate(value, is_empty)     # equivalent, via the pre-instantiated shortcut
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        hasattr(value, "__len__")
        and len(value) == 0
    )
```

On failure, the reported diagnostic distinguishes "this value doesn't support `len()`
at all" from "this value has a length, but it isn't zero" — the latter names the
actual length found.

[▲ Back to top](#-table-of-contents)

---

### `NotEmpty`

Value must **not** be empty, as reported by `len()` — the direct inverse of `IsEmpty`,
implemented independently rather than as `Not(IsEmpty())` for a slightly more direct
diagnostic message.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, NotEmpty())
validate(value, not_empty)     # equivalent, via the pre-instantiated shortcut
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        hasattr(value, "__len__")
        and len(value) > 0
    )
```

On failure, the reported diagnostic again distinguishes "no `len()` support at all"
from "has a length, but it's zero."

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#predicatescheckers--basic-state--identity)