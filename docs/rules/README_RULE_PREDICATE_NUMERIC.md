# 📦 `rules/predicates/numeric` — Numeric Type Identity Rules

The `numeric` package holds rules that check *what kind of number* a value is —
strict type checks for `bool`, `int`, `float`, `Decimal`, and the general numeric
umbrella, plus two special float states (`NaN`, infinity) and two specific-value
checks (`IsZero`, `IsPi`). This is the type layer numeric constraints (`arithmetic/`,
`comparisons/`) build on top of.

```python
from ..base_class import Rule

class IsInteger(Rule):
    ...
```

## A note on excluding `bool`

Every rule in this package that means "a real number" (`IsInteger`, `IsNumber`,
`IsPrimitiveNumber`, `IsZero`, `IsPi`) explicitly excludes `bool` via `and not
isinstance(value, bool)`, even though `bool` is technically a subclass of `int` in
Python (`isinstance(True, int)` is `True`). Without this exclusion, `IsInteger()` would
silently accept `True`/`False` as integers — almost never the intent when a rule says
"this must be a number." `IsBool` is the one rule in this package that goes the other
way, checking `isinstance(value, bool)` directly, for when a genuine boolean is what's
actually wanted.

## A note on `IsDecimal`

`IsDecimal` is the one rule here with no such carve-out to make — `Decimal` doesn't
subclass `int`/`float`, so a plain `isinstance(value, Decimal)` is already exact and
unambiguous.

---

## 🧭 Table of Contents

* [`IsBool`](#isbool)
* [`IsInteger`](#isinteger)
* [`IsFloat`](#isfloat)
* [`IsDecimal`](#isdecimal)
* [`IsNumber`](#isnumber)
* [`IsPrimitiveNumber`](#isprimitivenumber)
* [`IsZero`](#iszero)
* [`IsNan`](#isnan)
* [`IsInfinity`](#isinfinity)
* [`IsPi`](#ispi)
* [`IsEven`](#iseven)
* [`IsFinite`](#isfinite)
* [`IsOdd`](#isodd)

[⬅️ Back to main README](../../README.md#predicatesnumeric--numeric-type-identity)

---

### `IsBool`

Value must be a boolean — `True` or `False`, and nothing else.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsBool())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return isinstance(value, bool)
```

[▲ Back to top](#-table-of-contents)

---

### `IsInteger`

Value must be an `int` — explicitly excluding `bool`.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsInteger())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
    )
```

[▲ Back to top](#-table-of-contents)

---

### `IsFloat`

Value must be a `float`.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsFloat())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return isinstance(value, float)
```

> 💡 `IsFloat` alone accepts `float('nan')` and `float('inf')`, since both are,
> structurally, floats — see `IsNan`/`IsInfinity` below if you need to exclude them.

[▲ Back to top](#-table-of-contents)

---

### `IsDecimal`

Value must be a `decimal.Decimal`.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsDecimal())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return isinstance(value, Decimal)
```

[▲ Back to top](#-table-of-contents)

---

### `IsNumber`

Value must be any kind of number — `int`, `float`, `Decimal`, or `complex` —
explicitly excluding `bool`. The broadest numeric umbrella in this package.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsNumber())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, (int, float, Decimal, complex))
        and not isinstance(value, bool)
    )
```

[▲ Back to top](#-table-of-contents)

---

### `IsPrimitiveNumber`

Value must be `int` or `float` specifically — narrower than `IsNumber` (excludes
`Decimal` and `complex`), still excluding `bool`. Used internally throughout this
library (e.g. by `CloseTo`'s own parameter validation) wherever a check needs "an
ordinary number," not the full numeric tower.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsPrimitiveNumber())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )
```

[▲ Back to top](#-table-of-contents)

---

### `IsZero`

Numeric value must equal zero — accepts any type `IsNumber` would (`int`, `float`,
`Decimal`, `complex`), still excluding `bool`.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsZero())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, (int, float, Decimal, complex))
        and not isinstance(value, bool)
        and value == 0
    )
```

[▲ Back to top](#-table-of-contents)

---

### `IsNan`

Value must be a `float` NaN specifically — a thin wrapper around `math.isnan`, gated
by an explicit `isinstance(value, float)` check first (since `math.isnan` itself
requires a float-compatible argument).

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsNan())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, float)
        and math.isnan(value)
    )
```

On failure, the diagnostic distinguishes "this isn't a float at all" from "this is a
float, but a regular (non-NaN) one."

[▲ Back to top](#-table-of-contents)

---

### `IsInfinity`

Value must be positive or negative infinity — a thin wrapper around `math.isinf`, with
the same `isinstance(value, float)` gate as `IsNan`.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsInfinity())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, float)
        and math.isinf(value)
    )
```

On failure, the diagnostic distinguishes "this isn't a float at all" from "this is a
finite float."

[▲ Back to top](#-table-of-contents)

---

### `IsPi`

Value must equal `math.pi` when both are rounded to a given number of decimal places
— the one rule in this package with a constructor parameter, and the one that performs
its comparison via `round()` rather than a direct type/identity check. `math.pi`
rounded to `decimal_places` is precomputed once at construction, not on every
validation.

**Parameters:**
* `decimal_places` (*int*): Number of decimal places to round both the value and
  `math.pi` to before comparing. Must be a non-negative integer (validated at
  construction).

**Example usage:**
```python
validate(value, IsPi(decimal_places=5))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    try:
        return (
            isinstance(value, (int, float, Decimal))
            and not isinstance(value, bool)
            and round(float(value), self.decimal_places) == self._rounded_pi
        )
    except (TypeError, OverflowError, ValueError):
        return False
```

Casting to `float` before rounding lets `int` and `Decimal` values compare seamlessly
against the precomputed rounded `math.pi`, without needing separate comparison paths
per accepted type. On failure, the diagnostic distinguishes "this isn't a number at
all" from "this is a number, but rounds to something other than π at this precision" —
the latter states both the actual rounded value and the expected one.

[▲ Back to top](#-table-of-contents)

---

### `IsEven`

Value must be an even integer — explicitly excluding `bool`.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsEven())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value % 2 == 0
    )
```

On failure, the diagnostic distinguishes non-integer types from odd integers.

[▲ Back to top](#-table-of-contents)

---

### `IsFinite`

Value must be a finite primitive number (`int` or `float`) — explicitly excluding `bool`, `NaN`, and infinities.

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsFinite())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )
```

On failure, the diagnostic distinguishes non-numeric types from non-finite values (`NaN` or `+/-inf`).

[▲ Back to top](#-table-of-contents)

---

### `IsOdd`

Value must be an odd integer — explicitly excluding `bool`.

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsOdd())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value % 2 != 0
    )
```

On failure, the diagnostic distinguishes non-integer types from even integers.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#predicatesnumeric--numeric-type-identity)