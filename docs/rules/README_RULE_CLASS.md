# 🧩 `Rule` — Abstract Base Class for Validation Rules

`Rule` is the single foundation every validation rule in `simplibs-rules` is built
on — from the simplest type check (`IsString`) to the most elaborate composed
constraint (`AllOf(IsInteger(), GreaterThan(0))`). It does not implement any concrete
check itself; instead it provides four things every rule needs:

1. A minimal, mandatory contract every concrete rule must fulfill
(`is_valid`, `build_exception`).
2. A unified evaluation interface built on top of that contract — `validate()`, the
callable shorthand (`rule(value)`), and the various return modes.
3. Operator-based composition (`|`, `&`, `~`) that lets any two rules (or a rule and a
plain callable) combine into a new rule, without either side needing to know
anything about the other.
4. A bridge into Python's own typing system (`annotated()`), letting a rule attach
itself directly to a type hint that both static type checkers and this library's
own runtime tooling (`IsTyping`, `validate_call`, `validate_dataclass`) understand.

```python
from abc import ABC, abstractmethod
from typing import Annotated, Any, Callable, overload
from ._NotARule import _NotARule

class Rule(ABC):
    ...
```

## A note on why `Rule` is abstract

`Rule` can never be instantiated directly — `is_valid` and `build_exception` are
declared with `@abstractmethod` and carry no implementation of their own. This is
deliberate: `Rule` only defines *what every rule must be able to answer* (does this
value pass? what does failure look like?), never *how* — that answer is always
specific to the concrete rule (`IsInteger`, `HasLength`, `Regex`, ...). Every piece of
shared machinery this class *does* provide (`validate`, `__call__`, the operators,
`annotated`) is built purely on top of those two abstract methods, so any concrete
rule that implements them correctly gets the entire rest of this interface for free.

---

## 🧭 Table of Contents

* [`is_valid`](#is_valid)
* [`build_exception`](#build_exception)
* [`__call__`](#__call__)
* [`validate`](#validate)
* [`annotated`](#annotated)
* [`__or__` / `__ror__`](#__or__--__ror__)`
* [`__and__` / `__rand__`](#__and__--__rand__)`
* [`__invert__`](#__invert__)
* [The `__not_rule__` Hook & `_NotARule`](#the-__not_rule__-hook--_notarule)`

[⬅️ Back to main README](../../README.md#-the-rule-class)

---

### `is_valid`

**Abstract.** The single true source of "does this value satisfy the rule" for every
rule in the library. Every other method on `Rule` — `validate`, `__call__`, and every
composed rule's own `is_valid` (`AllOf`, `AnyOf`, `Not`, ...) — ultimately reduces to
calling this method somewhere.

**Parameters:**

* `value` (*Any*): The value being tested.

**Returns:**

* `bool`: `True` if `value` satisfies the rule, `False` otherwise. Must never raise —
a concrete rule that cannot cleanly evaluate a value (wrong type, missing attribute,
...) reports that as `False`, not as an exception. `UserRule` is the one place this
contract is actively *enforced* for external input: it catches any exception raised
by a wrapped user callable and converts it to `False`, exactly to preserve this
guarantee even for code this library didn't write.

**Example usage:**

```python
rule = IsInteger()
rule.is_valid(5)      # -> True
rule.is_valid("5")    # -> False
```

**Under the hood** *(as implemented by a concrete rule, e.g. `GreaterThan`)*:

```python
def is_valid(self, value: Any) -> bool:
    try:
        return value > self.threshold
    except TypeError:
        return False
```

[▲ Back to top](#-table-of-contents)

---

### `build_exception`

**Abstract.** Constructs — but does not raise — the diagnostic exception describing
*why* a value failed this rule. Called by `validate()` only after `is_valid()` has
already returned `False`; never called speculatively, and never itself re-evaluates
`is_valid()`.

**Parameters:**

* `value` (*Any*): The value that failed validation.
* `value_name` (*str | None*): The name of the parameter/variable being validated, for
diagnostic labeling.
* `context` (*str | None*): Additional free-text context describing where/why this
validation is happening.

**Returns:**

* `Exception`: A fully constructed (not raised) exception — by convention, a
`ValidateError` carrying `expected`, `problem`, and `how_to_fix` fields, but any
`Exception` subclass is acceptable.

**Example usage:**

```python
rule = GreaterThan(0)
if not rule.is_valid(-5):
    raise rule.build_exception(-5, value_name="age")
```

**Under the hood** *(as implemented by `AllOf`, a composed rule)*:

```python
def build_exception(self, value, value_name=None, context=None):
    for rule in self.rules:
        if not as_predicate(rule)(value):
            return build_child_exception(rule, value, value_name, context)
    # unreachable fallback — see AllOf's own design notes
```

[▲ Back to top](#-table-of-contents)

---

### `__call__`

Lets any rule instance be used directly as a plain predicate function — `rule(value)`
instead of `rule.is_valid(value)`. This is what makes a `Rule` instance interchangeable
with an ordinary callable everywhere this library accepts "a `Rule` or a callable"
(`validate()`, `AllOf`, `ForEach`, `override_rules`, ...).

**Parameters:**

* `value` (*Any*): The value being tested.

**Returns:**

* `bool`: Identical to `is_valid(value)`.

**Example usage:**

```python
is_positive = GreaterThan(0)

if is_positive(5):
    ...

# Interchangeable with a plain function wherever one is expected:
values = filter(is_positive, [-2, -1, 0, 1, 2])
```

**Under the hood:**

```python
def __call__(self, value: Any) -> bool:
    return self.is_valid(value)
```

[▲ Back to top](#-table-of-contents)

---

### `validate`

The primary, everyday evaluation entry point — and the only method on `Rule` that can
raise. Every `validate_*` function and the `validate()` top-level function ultimately
delegate here for any `Rule` instance.

**Parameters:**

* `value` (*Any*): The value being tested.
* `value_name` (*str | None*, keyword-only): Passed straight through to
`build_exception` on failure.
* `context` (*str | None*, keyword-only): Passed straight through to `build_exception`
on failure.
* `return_bool` (*bool*, keyword-only, default `False`): If `True`, returns `False` on
failure instead of raising.
* `return_value` (*bool*, keyword-only, default `False`): If `True` **and** validation
passes, returns `value` itself instead of `True`.

**Returns:**

* `Any`: `value` (if `return_value=True` and passing), `True` (if passing and
`return_value=False`), or `False` (if failing and `return_bool=True`).

**Raises:**

* `Exception`: Whatever `build_exception(...)` constructs, if validation fails and
`return_bool=False` (the default).

**Example usage:**

```python
rule = IsInteger() & GreaterThan(0)

rule.validate(5)                          # -> True
rule.validate(5, return_value=True)       # -> 5
rule.validate(-5, return_bool=True)       # -> False (no exception)
rule.validate(-5)                         # -> raises ValidateError
```

**Under the hood:**

```python
def validate(self, value, *, value_name=None, context=None,
             return_bool=False, return_value=False):
    if self.is_valid(value):
        return value if return_value else True

    if return_bool:
        return False

    raise self.build_exception(value, value_name=value_name, context=context)
```

[▲ Back to top](#-table-of-contents)

---

### `annotated`

Wraps this rule as `typing.Annotated[type_, self]` — the bridge that lets a `Rule`
attach itself directly to a type hint, readable both by static type checkers (which
see `type_` and ignore the metadata) and by this library's own runtime annotation
decomposition (`IsTyping`, `validate_call`, `validate_dataclass`), which unpacks the
`Rule` back out of the metadata to enforce it at call time.

**Parameters:**

* `type_` (*type*): The underlying type the annotation should present to static
tooling (e.g. `int`, `str`).

**Returns:**

* `Any`: `Annotated[type_, self]` — an ordinary typing construct, usable anywhere a
type hint is accepted.

**Example usage:**

```python
PositiveInt = (is_integer & greater_than(0)).annotated(int)

def register(age: PositiveInt) -> None:
    ...

@validate_call
def create_user(age: PositiveInt) -> None:
    ...   # age is validated automatically on every call
```

> 💡 For building a named type from a *fresh* rule (rather than one you already have an
> instance of), `validated_type(type_, *rules)` is usually the more direct spelling of
> the same idea — see its own documentation in `docs/tools/`.

**Under the hood:**

```python
def annotated(self, type_: type) -> Any:
    return Annotated[type_, self]
```

[▲ Back to top](#-table-of-contents)

---

### `__or__` / `__ror__`

Combines this rule with another rule or plain callable via logical OR — `rule1 | rule2`
passes if **either** side does. Equivalent to `AnyOf(rule1, rule2)`.

**Parameters:**

* `other` (*Rule | Callable[[Any], bool] | _NotARule*): The right-hand operand.

**Returns:**

* `Rule`: `AnyOf(self, other)` (via `__or__`) or `AnyOf(other, self)` (via `__ror__`,
when `other` is on the left and doesn't itself know how to combine with a `Rule`).
* `Any`: Handed over to external object's reflected operator if `other` satisfies `_NotARule`.
* `NotImplemented`: If `other` is neither a `Rule` instance nor an accepted callable — Python then
falls back to `other`'s own reflected method, or raises `TypeError` as usual.

**Example usage:**

```python
is_int_or_bool = is_integer | is_bool

is_int_or_bool.validate(True)   # -> True
is_int_or_bool.validate("x")    # -> raises
```

**Under the hood:**

```python
@overload
def __or__(self, other: _NotARule) -> Any: ...
@overload
def __or__(self, other: "Rule | Callable[[Any], bool]") -> "Rule": ...
def __or__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
    if isinstance(other, Rule) or (
        callable(other) and not hasattr(other, "__not_rule__")
    ):
        from ..containers.AnyOf import AnyOf
        return AnyOf(self, other)
    return NotImplemented

@overload
def __ror__(self, other: _NotARule) -> Any: ...
@overload
def __ror__(self, other: "Rule | Callable[[Any], bool]") -> "Rule": ...
def __ror__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
    if isinstance(other, Rule) or (
        callable(other) and not hasattr(other, "__not_rule__")
    ):
        from ..containers.AnyOf import AnyOf
        return AnyOf(other, self)
    return NotImplemented
```

> `AnyOf`/`AllOf` imports are deferred inside the method body, not at module level —
> see [Design Notes: Lazy Imports](#a-note-on-lazy-container-imports) below.

[▲ Back to top](#-table-of-contents)

---

### `__and__` / `__rand__`

Combines this rule with another rule or plain callable via logical AND — `rule1 & rule2` 
passes only if **both** sides do. Equivalent to `AllOf(rule1, rule2)`.

**Parameters:**

* `other` (*Rule | Callable[[Any], bool] | _NotARule*): The right-hand operand.

**Returns:**

* `Rule`: `AllOf(self, other)` (via `__and__`) or `AllOf(other, self)` (via `__rand__`).
* `Any`: Handed over to external object's reflected operator if `other` satisfies `_NotARule`.
* `NotImplemented`: If `other` is neither a `Rule` instance nor an accepted callable.

**Example usage:**

```python
positive_int = is_integer & greater_than(0)

positive_int.validate(5)     # -> True
positive_int.validate(-5)    # -> raises
```

**Under the hood:**

```python
@overload
def __and__(self, other: _NotARule) -> Any: ...
@overload
def __and__(self, other: "Rule | Callable[[Any], bool]") -> "Rule": ...
def __and__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
    if isinstance(other, Rule) or (
        callable(other) and not hasattr(other, "__not_rule__")
    ):
        from ..containers.AllOf import AllOf
        return AllOf(self, other)
    return NotImplemented

@overload
def __rand__(self, other: _NotARule) -> Any: ...
@overload
def __rand__(self, other: "Rule | Callable[[Any], bool]") -> "Rule": ...
def __rand__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
    if isinstance(other, Rule) or (
        callable(other) and not hasattr(other, "__not_rule__")
    ):
        from ..containers.AllOf import AllOf
        return AllOf(other, self)
    return NotImplemented
```

[▲ Back to top](#-table-of-contents)

---

### `__invert__`

Negates this rule via `~rule`. Equivalent to `Not(self)`.

**Parameters:**

* *(none — takes only `self`)*

**Returns:**

* `Rule`: `Not(self)`.

**Example usage:**

```python
not_blank = ~is_blank

not_blank.validate("hello")   # -> True
not_blank.validate("   ")     # -> raises
```

**Under the hood:**

```python
def __invert__(self) -> "Rule":
    from ..containers.Not import Not
    return Not(self)
```

[▲ Back to top](#-table-of-contents)

---

### The `__not_rule__` Hook & `_NotARule`

Callable objects carrying the `__not_rule__` attribute marker are explicitly excluded 
from being wrapped as plain predicate functions in `AllOf` or `AnyOf`.

Instead, binary operators check `callable(other) and not hasattr(other, "__not_rule__")`. 
If the marker is present, `Rule.__and__` and `Rule.__or__` return `NotImplemented`, 
ceding control to Python's reflected operator protocol (`other.__rand__` / `other.__ror__`).

To ensure static type checkers resolve signatures accurately:

1. `_NotARule` is defined as a structural `Protocol` matching any callable with `__not_rule__`.
2. The `@overload` for `_NotARule` is placed **first** to prevent type checkers from matching 
3. non-rule callables (such as `Action`) as standard `Callable[[Any], bool]` functions.

[▲ Back to top](#-table-of-contents)

---

## A note on lazy container imports

`AnyOf`, `AllOf`, and `Not` are imported *inside* each operator method's body, not at
the top of this module. `rules/containers/` imports `Rule` from `rules/base_class`
already — a module-level import here would create a circular import. Deferring the
import to the moment an operator is actually used breaks that cycle, at the (one-time,
per operator call) cost of a repeated `import` statement — negligible compared to the
cost of evaluating the rule itself.

## A note on operator chaining and flattening

Chained operators evaluate left-to-right, so `a & b & c` builds as `(a & b) & c`, which
would naively nest as `AllOf(AllOf(a, b), c)`. Rather than handling this here, `AllOf`
and `AnyOf` each flatten same-type nested instances in their own constructors — so this
class stays a pure, one-line delegation regardless of how many operators are chained.
See `AllOf`'s own documentation for the flattening mechanics.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-the-rule-class)