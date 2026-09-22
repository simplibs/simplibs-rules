from abc import ABC, abstractmethod
from typing import Annotated, Any, Callable, overload

# Inners
from ._NotARule import _NotARule


class Rule(ABC):
    """Abstract base class for all validation rules.

    Every concrete rule inherits from this class and implements `is_valid` and `build_exception`.
    The class also provides a unified evaluation interface via `validate`, the magic `__call__` method,
    and Python typing integration via `annotated`.
    """

    # ----------------------------------------------------------------------
    # 1) Abstract Interface (mandatory for subclasses)
    # ----------------------------------------------------------------------

    @abstractmethod
    def is_valid(
        self,
        value: Any,
    ) -> bool:
        """Return True if the tested value satisfies the rule, otherwise False."""
        raise NotImplementedError

    @abstractmethod
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        """Create and return an exception instance (SimpleException) describing the validation failure."""
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 2) Public Interface & Evaluation Logic
    # ----------------------------------------------------------------------

    def __call__(
        self,
        value: Any,
    ) -> bool:
        """Allow using the rule instance directly as a predicate function.

        Returns the boolean result of `is_valid(value)`.
        """
        return self.is_valid(value)

    def validate(
        self,
        value: Any,
        *,
        value_name: str | None = None,
        context: str | None = None,
        return_bool: bool = False,
        return_value: bool = False,
    ) -> Any:
        """Validate a value against this rule.

        Based on parameter flags, returns the original value, True/False,
        or raises a structured exception constructed by `build_exception`.

        Args:
            value: The tested value.
            value_name: The name of the validated parameter/variable for diagnostic reporting.
            context: Additional context describing the validation environment.
            return_bool: If True, returns False on failure instead of raising an exception.
            return_value: If validation passes and this is True, returns original `value` instead of `True`.

        Returns:
            Returns `value`, `True`, or `False` depending on parameter flags.

        Raises:
            Exception: If validation fails and `return_bool` is False.
        """
        if self.is_valid(value):
            return value if return_value else True

        if return_bool:
            return False

        raise self.build_exception(
            value,
            value_name=value_name,
            context=context,
        )

    # ----------------------------------------------------------------------
    # 3) Typing Integration
    # ----------------------------------------------------------------------

    def annotated(self, type_: type) -> Any:
        """Wrap this rule as `typing.Annotated[type_, self]` for type hints.

        Enables seamless integration with static type checkers (MyPy, Pyright)
        and runtime annotation inspection (e.g., IsTyping or decorator engines).

        Args:
            type_: The target base type (e.g., int, str, float).

        Returns:
            An `Annotated` type hint combining the base type and this rule as metadata.
        """
        return Annotated[type_, self]

    # ----------------------------------------------------------------------
    # 4) Operator-Based Composition (|, &, ~)
    # ----------------------------------------------------------------------
    #
    # Each binary operator defines two @overload variants:
    #   1) `_NotARule` (anything carrying `__not_rule__`, e.g. `Action`) -> `Any`
    #      MUST come first — otherwise MyPy would structurally match `Action`
    #      against `Callable[[Any], bool]` in the second variant (since Action is a one-arg
    #      callable returning `Any`, which satisfies `bool`) and mistakenly return `Rule`
    #      where execution actually falls back to `other.__rand__` at runtime.
    #   2) `Rule | Callable[[Any], bool]` -> `Rule` — standard, documented behavior.
    # The concrete method implementation below overloads remains unchanged.

    @overload
    def __or__(self, other: _NotARule) -> Any: ...
    @overload
    def __or__(self, other: "Rule | Callable[[Any], bool]") -> "Rule": ...
    def __or__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Combine with another rule/callable via logical OR: `rule1 | rule2`.

        Equivalent to `AnyOf(self, other)`. Returns `NotImplemented` if `other`
        is neither a `Rule` instance nor an accepted callable, letting Python fall
        back to `other.__ror__(self)` or raise `TypeError` as usual.
        """
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
        """Support `other | rule` when `other` has no (or a declining) `__or__`."""
        if isinstance(other, Rule) or (
            callable(other) and not hasattr(other, "__not_rule__")
        ):
            from ..containers.AnyOf import AnyOf

            return AnyOf(other, self)
        return NotImplemented

    @overload
    def __and__(self, other: _NotARule) -> Any: ...
    @overload
    def __and__(self, other: "Rule | Callable[[Any], bool]") -> "Rule": ...
    def __and__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Combine with another rule/callable via logical AND: `rule1 & rule2`.

        Equivalent to `AllOf(self, other)`. Returns `NotImplemented` if `other`
        is neither a `Rule` instance nor an accepted callable, letting Python fall
        back to `other.__rand__(self)` or raise `TypeError` as usual.
        """
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
        """Support `other & rule` when `other` has no (or a declining) `__and__`."""
        if isinstance(other, Rule) or (
            callable(other) and not hasattr(other, "__not_rule__")
        ):
            from ..containers.AllOf import AllOf

            return AllOf(other, self)
        return NotImplemented

    def __invert__(self) -> "Rule":
        """Negate this rule via `~rule`. Equivalent to `Not(self)`."""
        from ..containers.Not import Not

        return Not(self)


_DESIGN_NOTES = """
# Rule — Base Abstract Class for Validation Rules

## Purpose
The `Rule` class serves as the fundamental pillar of the entire
`simplibs-rules` library. It defines a standardized interface for
evaluating conditions, assembling structured exceptions (`SimpleException`),
and bridging validation rules with Python's typing system.

---

## 1. Architectural Principles & Minimalism

### Single Responsibility
* **Evaluation Scope:** The `Rule` class is exclusively concerned with
  whether a value satisfies the condition (`is_valid`) and how the exception
  card looks on failure (`build_exception`).
* **`None` Value Handling:** The rule itself does not special-case `None`.
  If `None` needs to be treated as a valid value, compose it explicitly
  with `IsNone` (e.g. `rule | IsNone()`) rather than relying on a global
  flag.

### Zero Import-Time Overhead
* Unnecessary metaclass inspection routines have been removed in accordance with
  the **Programmer's Zen** philosophy. Documentation and usage examples are
  audited via automated unit tests rather than import-time hooks.

---

## 2. Core Methods

### `is_valid(value) -> bool`
* Pure abstract method.
* Must never raise exceptions for standard validation failures—always
  returns strictly `True` or `False`.

### `build_exception(value, value_name, context) -> Exception`
* Constructs and returns an exception instance (typically from the
  `simplibs-exception` family).
* The exception is only **assembled and returned**, not raised directly in
  this method.

### `__call__(value) -> bool`
* Callable magic method enabling direct predicate invocation.

### `validate(value, ...)`
* Primary evaluation method offering a flexible return interface:
1. Value passes & `return_value=True` -> returns `value`.
2. Value passes & `return_value=False` -> returns `True`.
3. Value fails & `return_bool=True` -> returns `False`.
4. Value fails & `return_bool=False` -> raises exception from
`build_exception(...)`.

---

## 3. Typing System Integration (`annotated`)

Bridges runtime validation rules directly into Python's standard type
annotation machinery via `typing.Annotated` (PEP 593) — see `annotated()`
docstring and `validated_type()` for the named-type equivalent.

---

## 4. Operator-Based Composition (`|`, `&`, `~`)

* **`rule1 | rule2`** (`__or__` / `__ror__`) -> `AnyOf(rule1, rule2)`.
* **`rule1 & rule2`** (`__and__` / `__rand__`) -> `AllOf(rule1, rule2)`.
* **`~rule`** (`__invert__`) -> `Not(rule)`.
* **Lazy Imports:** Container imports (`AnyOf`, `AllOf`, `Not`) are deferred
  inside method bodies to prevent circular import issues.
* **`NotImplemented` Fallback:** Binary operators return `NotImplemented` for
  unsupported types, allowing Python's standard reflected operator
  protocols to execute naturally.

---

## 5. The `__not_rule__` Hook — Opting Out of Rule-Side Composition

`__not_rule__` is a bare class-level marker — its *presence*, not its
value, is what matters. `Rule.__and__`/`__or__`/`__rand__`/`__ror__` check
`callable(other) and not hasattr(other, "__not_rule__")` before treating
`other` as a plain predicate to fold into `AllOf`/`AnyOf`. Any callable
carrying this marker (e.g. `simplibs-actions`' `Action`) is
deliberately excluded and gets `NotImplemented` instead, handing control
back to Python's operator protocol — which then tries `other`'s own
reflected method.

Any future callable class with the same need — composable, but meant to
*consume and orchestrate* rules rather than be silently folded into
one — should carry the same `__not_rule__` marker.

---

## 6. Typing the `__not_rule__` Split — `_NotARule` Protocol, Not an Import

`Rule.py`'s overloads need to tell a type checker "when `other` carries
`__not_rule__`, don't assume this returns `Rule`" — but `Rule` lives in
`simplibs-rules`, a lower layer that downstream packages build on top
of. Importing higher-level abstractions here (even under `TYPE_CHECKING`)
would introduce a reverse dependency.

`_NotARule` is a structural `Protocol` (`__not_rule__: Any` + a one-arg
`__call__`) instead — it matches `Action` (and anything shaped like it)
without `Rule` ever needing to know it exists. The overload
returns `Any` for this case rather than a precise type, because `Rule`
genuinely does not know what `other.__rand__`/`__ror__` will produce.

**Overload ordering matters and is not cosmetic.** The `_NotARule`
overload is listed *first* on every operator. `@overload` resolution is
first-match, top-to-bottom — and `Action` structurally satisfies
`Callable[[Any], bool]` too (it's callable with one positional argument;
its `Any` return is compatible with an expected `bool`). Without the
`_NotARule` overload coming first, a type checker would silently match
`Action` against the generic callable overload and infer `Rule` as the
result of `rule & action` — which is wrong the moment `Rule.__and__`
actually returns `NotImplemented` and execution falls through to
`Action.__rand__` at runtime. Putting the exclusion case first prevents
that false precision.

---

## 7. Ecosystem Integration

* **`simplibs-exception`:** `build_exception` utilizes `value_name` as `label`,
`context`, and `value` to format readable diagnostic cards.
* **`IsTyping`:** Automatically extracts `Rule` instances attached
via `.annotated()` to decompose typing constructs into composed validation trees.
"""