# 📦 `rules/predicates/comparisons` — Ordering & Equality Rules

The `comparisons` package holds the general-purpose relational rules every other
numeric/comparable-type rule builds on top of — strict/inclusive ordering (`<`, `<=`,
`>`, `>=`), range membership, and equality/inequality. Unlike `arithmetic/`, these
rules work with **any** comparable type, not just numbers — `LessThan("m")` against
strings, or `InRange(date(2020, 1, 1), date(2020, 12, 31))` against dates, are both
perfectly valid uses.

```python
from ..base_class import Rule

class GreaterThan(Rule):
    ...
```

## A note on incomparable types

Every ordering rule in this package (`GreaterThan`, `GreaterOrEqual`, `LessThan`,
`LessOrEqual`, `InRange`) wraps its comparison in a `try/except TypeError`. Python
raises `TypeError` when two values simply can't be ordered against each other (e.g.
`5 > "a"`) — rather than letting that propagate out of what's meant to be a pure
boolean check, `is_valid` catches it and reports `False`. `build_exception` then
re-attempts the same comparison to determine *which* of two distinct diagnostics
applies: "the types are comparable, but the value is on the wrong side" vs. "these
types can't be compared with each other at all" — the latter reported as a `TypeError`
naming both types involved, the former as an ordinary `ValueError`.

---

## 🧭 Table of Contents

* [`Equals`](#equals)
* [`NotEquals`](#notequals)
* [`GreaterThan`](#greaterthan)
* [`GreaterOrEqual`](#greaterorequal)
* [`LessThan`](#lessthan)
* [`LessOrEqual`](#lessorequal)
* [`InRange`](#inrange)

[⬅️ Back to main README](../../README.md#predicatescomparisons--ordering--equality)

---

### `Equals`

Value must be strictly equal (`==`) to a given target.

**Parameters:**
* `expected_value` (*Any*): The value to compare against.

**Example usage:**
```python
validate(value, Equals("active"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return value == self.expected_value
```

[▲ Back to top](#-table-of-contents)

---

### `NotEquals`

Value must **not** be equal (`!=`) to a given forbidden value.

**Parameters:**
* `forbidden` (*Any*): The value the input must not equal.

**Example usage:**
```python
validate(value, NotEquals(0))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return value != self.forbidden
```

[▲ Back to top](#-table-of-contents)

---

### `GreaterThan`

Value must be strictly greater than (`>`) a given threshold.

**Parameters:**
* `threshold` (*Any*): The value to compare against.

**Example usage:**
```python
validate(value, GreaterThan(0))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        return value > self.threshold
    except TypeError:
        return False
```

[▲ Back to top](#-table-of-contents)

---

### `GreaterOrEqual`

Value must be greater than or equal to (`>=`) a given threshold.

**Parameters:**
* `threshold` (*Any*): The value to compare against.

**Example usage:**
```python
validate(value, GreaterOrEqual(0))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        return value >= self.threshold
    except TypeError:
        return False
```

[▲ Back to top](#-table-of-contents)

---

### `LessThan`

Value must be strictly less than (`<`) a given threshold.

**Parameters:**
* `threshold` (*Any*): The value to compare against.

**Example usage:**
```python
validate(value, LessThan(100))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        return value < self.threshold
    except TypeError:
        return False
```

[▲ Back to top](#-table-of-contents)

---

### `LessOrEqual`

Value must be less than or equal to (`<=`) a given threshold.

**Parameters:**
* `threshold` (*Any*): The value to compare against.

**Example usage:**
```python
validate(value, LessOrEqual(100))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        return value <= self.threshold
    except TypeError:
        return False
```

[▲ Back to top](#-table-of-contents)

---

### `InRange`

Value must fall within an inclusive or exclusive range, with each boundary's
inclusivity independently configurable. Rejects an inverted range (`min_val >
max_val`) at construction — and, if the two boundary values can't even be compared to
each other, reports that as its own distinct construction-time error rather than
letting an unrelated `TypeError` surface.

**Parameters:**
* `min_val` (*Any*): The lower boundary.
* `max_val` (*Any*): The upper boundary.
* `include_min` (*bool*, default `True`): Whether `min_val` itself is an accepted value.
* `include_max` (*bool*, default `True`): Whether `max_val` itself is an accepted value.

**Example usage:**
```python
validate(value, InRange(1, 10))
validate(value, InRange(0.0, 1.0, include_min=True, include_max=False))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        if self.include_min:
            if value < self.min_val:
                return False
        else:
            if value <= self.min_val:
                return False

        if self.include_max:
            if value > self.max_val:
                return False
        else:
            if value >= self.max_val:
                return False

        return True
    except TypeError:
        return False
```

On failure, the reported diagnostic renders the range using standard interval bracket
notation matching each boundary's inclusivity — `[1, 10]` for fully inclusive,
`[0.0, 1.0)` for an excluded upper bound, and so on — alongside the same "incomparable
types" vs. "out of range" distinction the other comparison rules in this package draw.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#predicatescomparisons--ordering--equality)