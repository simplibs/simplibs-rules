# 📦 `rules/predicates/arithmetic` — Numeric Relationship Rules

The `arithmetic` package holds rules that check a *relationship* a number has to
another number — approximate equality within a tolerance, divisibility, and exact
remainders — as opposed to the simple type/comparison checks covered elsewhere
(`comparisons/`, `numeric/`). All three rules here work on `int`/`float` and explicitly
exclude `bool` (since `bool` is a subtype of `int` in Python, and `True`/`False` are
never meaningful as arithmetic operands for any of these checks).

```python
from ..base_class import Rule

class CloseTo(Rule):
    ...
```

---

## 🧭 Table of Contents

* [`CloseTo`](#closeto)
* [`DivisibleBy`](#divisibleby)
* [`HasRemainder`](#hasremainder)

[⬅️ Back to main README](../../README.md#predicatesarithmetic--numeric-relationships)

---

### `CloseTo`

Value must be numerically close to a target, within a relative and/or absolute
tolerance — the standard way to compare floats without falling into exact-equality
pitfalls (`0.1 + 0.2 != 0.3`). Built directly on Python's own `math.isclose`.

**Parameters:**
* `target` (*float | int*): The value being compared against.
* `rel_tol` (*float*, keyword-only, default `1e-9`): Relative tolerance, passed straight
  through to `math.isclose`.
* `abs_tol` (*float*, keyword-only, default `0.0`): Absolute tolerance, passed straight
  through to `math.isclose`.

**Example usage:**
```python
validate(value, CloseTo(math.pi, rel_tol=0.001))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isclose(value, self.target, rel_tol=self.rel_tol, abs_tol=self.abs_tol)
    )
```

On failure, the reported diagnostic distinguishes "this isn't a primitive number at
all" from "this is a number, but outside tolerance" — the latter names both the
relative tolerance and, if set above `0.0`, the absolute tolerance too.

[▲ Back to top](#-table-of-contents)

---

### `DivisibleBy`

Value must be evenly divisible by a given divisor — a plain `int`-only counterpart to
`CloseTo`, for exact rather than approximate numeric relationships.

**Parameters:**
* `divisor` (*int*): The divisor to check against. Must be a non-zero integer
  (validated at construction).

**Example usage:**
```python
validate(value, DivisibleBy(3))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value % self.divisor == 0
    )
```

On failure, the reported diagnostic distinguishes "this isn't an integer at all" from
"this is an integer, but not a multiple of `divisor`" — the latter suggests a concrete
example multiple as part of the fix.

[▲ Back to top](#-table-of-contents)

---

### `HasRemainder`

Value must produce a specific remainder when divided by a given divisor — a
generalization of `DivisibleBy` (`DivisibleBy(n)` is equivalent in spirit to
`HasRemainder(n, 0)`, though implemented independently), useful for "every 3rd item"
or "odd/even" style constraints (`HasRemainder(2, 1)` for odd numbers).

**Parameters:**
* `divisor` (*int*): The divisor to check against. Must be a non-zero integer.
* `remainder` (*int*): The exact remainder the value must produce. Must satisfy
  `0 <= remainder < abs(divisor)` — a remainder outside that range could never be
  produced by `%` for the given divisor, and is rejected at construction rather than
  silently accepted as an always-failing rule.

**Example usage:**
```python
validate(value, HasRemainder(divisor=3, remainder=1))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value % self.divisor == self.remainder
    )
```

On failure, the reported diagnostic shows the value's *actual* remainder alongside the
expected one (`"has remainder 2 when divided by 3, but expected 1"`), and suggests a
concrete example value that would satisfy the rule.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#predicatesarithmetic--numeric-relationships)