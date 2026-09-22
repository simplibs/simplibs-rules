# ⚖️ `simplibs-rules`

**Composable, explicit validation rules — pure predicates, zero transformation.**

A lightweight, high-performance Python library defining atomic, composable validation 
rules built on a clean `Rule` abstraction. Rules combine naturally with plain 
Python operators (`|`, `&`, `~`), carry structured, human-readable diagnostics 
on failure via `simplibs-exception`, and — through integrated type 
decomposition — understand Python's typing annotations natively.

```python
from simplibs.rules import is_integer, greater_than, IsTyping

# Operator composition
positive_int = is_integer & greater_than(0)

positive_int.is_valid(5)       # -> True
positive_int.is_valid(-5)      # -> False

# Type annotation decomposition
rule = IsTyping(list[int] | None)
rule.is_valid([1, 2, 3])       # -> True
rule.is_valid(["1", "2"])      # -> False
```

---

## 🧭 The Core Philosophy

Most validation approaches force a choice: write ad-hoc `if`/`raise` checks scattered 
through your codebase, or adopt heavy data-transformation frameworks. 
`simplibs-rules` is a **pure predicate engine**. A `Rule` never transforms or coerces 
a value; it only ever answers *"does this value satisfy me?"* and, on failure, 
provides structured, precise diagnostic exceptions.

Every rule is a small, composable object. You combine them with plain Python 
operators instead of writing nested configuration or custom functions:

```python
is_string & has_length(min_length=3) & not_blank
```

By decoupling rule definitions and evaluation logic from validation 
invocation wrappers, `simplibs-rules` serves as the foundational rule engine 
for higher-level validation tools (such as `simplibs-type` and `simplibs-validate`).

---

## 📦 Installation

```bash
pip install simplibs-rules
```

---

## 🚀 Quick Start in 60 Seconds

### Level 1: Evaluating rules directly

```python
from simplibs.rules import is_integer, greater_than

rule = is_integer & greater_than(0)

rule.is_valid(5)      # -> True
rule.is_valid(-5)     # -> False

# Raising structured exceptions
if not rule.is_valid(-5):
    raise rule.build_exception(-5, value_name="age")
```

### Level 2: Rule execution with return options

```python
rule = is_integer & greater_than(0)

rule.validate(5)                          # -> True
rule.validate(5, return_value=True)       # -> 5
rule.validate(-5, return_bool=True)       # -> False
rule.validate(-5)                         # -> raises ValidateError
```

### Level 3: Annotation-driven rules

```python
from simplibs.rules import IsTyping, build_typing_rule

# Converts complex typing constructs directly into rule trees:
typing_rule = IsTyping(dict[str, int])

typing_rule.is_valid({"apples": 5, "oranges": 10})   # -> True
typing_rule.is_valid({"apples": "5"})                # -> False
```

### Level 4: Unconditional direct triggers

When control flow guards in your application have already detected a failure condition inline, use `raise_invalid()` to bypass rule evaluation entirely and construct the diagnostic exception immediately:

```python
from simplibs.rules import raise_invalid, is_integer

value = -5

if value < 0:
    # Bypasses evaluation and directly raises the structured exception card
    raise_invalid(value, is_integer, value_name="age", context="Must be non-negative")
```

---

## 🛠️ Architecture & Package Structure

```
src/simplibs/rules/
├── base_class/             ◄── Abstract base class Rule & internal helpers (_NotARule)
│   ├── Rule.py
│   └── _NotARule.py
├── containers/             ◄── Rule combinators (AllOf, AnyOf, Not, NoneOf, ForEach, Compose)
├── predicates/             ◄── Single-purpose predicate rules
│   ├── arithmetic/         ◄── CloseTo, DivisibleBy, HasRemainder
│   ├── checkers/           ◄── IsEmpty, NotEmpty, IsNone, IsTrue, IsFalse
│   ├── collections/        ◄── IsContainer, HasItem, HasKey, HasKeys, AllUnique, IsSubsetOf, IsSupersetOf
│   ├── comparisons/        ◄── Equals, NotEquals, GreaterThan, GreaterOrEqual, LessThan, LessOrEqual, InRange
│   ├── introspection/      ◄── IsInstance, IsType, IsSubclass, IsDataclass, IsCallable, IsHashable, IsIterable, HasAttribute, HasLength
│   ├── logic/              ◄── Is, IsNot, IsIn, NotIn, UserRule
│   ├── numeric/            ◄── IsBool, IsInteger, IsFloat, IsDecimal, IsNumber, IsPrimitiveNumber, IsZero, IsNan, IsInfinity, IsPi
│   ├── strings/            ◄── IsString, Contains, IsSubstringOf, StartsWith, EndsWith, Regex, IsBlank, NotBlank
│   └── typing/             ◄── Annotation-driven evaluation (IsAny, IsTyping, build_typing_rule)
├── tools/                  ◄── Operational helper utilities
│   └── raise_invalid.py    ◄── Unconditional exception trigger (bypasses logic evaluation)
└── testing/                ◄── Testing contracts for Rule implementations
    └── assert_rule_contract.py
```

---

## 🧩 The `Rule` Class

Every rule in this library inherits from `Rule`. It defines the mandatory 
contract (`is_valid`, `build_exception`) and provides full composition 
capabilities out of the box.

```python
class Rule(ABC):

    @abstractmethod
    def is_valid(self, value: Any) -> bool:
        """Return True if the tested value satisfies the rule, otherwise False."""
        raise NotImplementedError

    @abstractmethod
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        """Create and return a structured exception describing the validation failure."""
        raise NotImplementedError

    def __call__(self, value: Any) -> bool:
        """Allow using the rule instance directly as a predicate function."""
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
        """Validate a value against this rule."""
        if self.is_valid(value):
            return value if return_value else True

        if return_bool:
            return False

        raise self.build_exception(value, value_name=value_name, context=context)

    def annotated(self, type_: type) -> Any:
        """Wrap this rule as `typing.Annotated[type_, self]` for type hints."""
        return Annotated[type_, self]

    # Operators for logical composition with @overload support for non-rule callables
    @overload
    def __or__(self, other: _NotARule) -> Any: ...
    @overload
    def __or__(self, other: Rule | Callable[[Any], bool]) -> Rule: ...

    @overload
    def __and__(self, other: _NotARule) -> Any: ...
    @overload
    def __and__(self, other: Rule | Callable[[Any], bool]) -> Rule: ...

    def __invert__(self) -> Rule: ...
```

➡️ Full method-by-method reference: [README_RULE_CLASS](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_CLASS.md)

---

## 📖 Rule Quick Reference

Every built-in `Rule` is exposed in two ways: as its **class** (`IsInteger`), 
and as a **snake_case shortcut** (`is_integer`) — a pre-instantiated object 
for zero-parameter rules, or the class itself for parameterized ones. 
Both are fully interchangeable.

### `containers/` — Composing other rules

| Class     | Shortcut   | Description / Parameters                                     |
|-----------|------------|--------------------------------------------------------------|
| `AllOf`   | `all_of`   | Logical AND across multiple rules (`*rules`). Behind `&`.    |
| `AnyOf`   | `any_of`   | Logical OR across multiple rules (`*rules`). Behind `        |`. |
| `Compose` | `compose`  | Transforms value before checking (`transformer, validator`). |
| `ForEach` | `for_each` | Validates every item in an iterable (`rule`).                |
| `NoneOf`  | `none_of`  | Value must satisfy none of the given rules (`*rules`).       |
| `Not`     | `negate`   | Logical NOT for a single rule (`rule`). Behind `~`.          |

➡️ [README_RULE_CONTAINERS](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_CONTAINERS.md)

### `predicates/` — Atomic predicates

* **`arithmetic/`**: `CloseTo`, `DivisibleBy`, `HasRemainder` — [README](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_PREDICATE_ARITHMETIC.md)
* **`checkers/`**: `IsEmpty`, `NotEmpty`, `IsNone`, `IsTrue`, `IsFalse` — [README](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_PREDICATE_CHECKERS.md)
* **`collections/`**: `IsContainer`, `HasItem`, `HasKey`, `HasKeys`, `AllUnique`, `IsSubsetOf`, `IsSupersetOf` — [README](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_PREDICATE_COLLECTIONS.md)
* **`comparisons/`**: `Equals`, `NotEquals`, `GreaterThan`, `GreaterOrEqual`, `LessThan`, `LessOrEqual`, `InRange` — [README](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_PREDICATE_COMPARISONS.md)
* **`introspection/`**: `IsInstance`, `IsType`, `IsSubclass`, `IsDataclass`, `IsCallable`, `IsHashable`, `IsIterable`, `HasAttribute`, `HasLength` — [README](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_PREDICATE_INTROSPECTION.md)
* **`logic/`**: `Is`, `IsNot`, `IsIn`, `NotIn`, `UserRule` — [README](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_PREDICATE_LOGIC.md)
* **`numeric/`**: `IsBool`, `IsInteger`, `IsFloat`, `IsDecimal`, `IsNumber`, `IsPrimitiveNumber`, `IsZero`, `IsNan`, `IsInfinity`, `IsPi` — [README](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_PREDICATE_NUMERIC.md)
* **`strings/`**: `IsString`, `Contains`, `IsSubstringOf`, `StartsWith`, `EndsWith`, `Regex`, `IsBlank`, `NotBlank` — [README](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_PREDICATE_STRINGS.md)

### `predicates/typing/` — Annotation-driven evaluation

| Class / Function    | Shortcut    | Description                                            |
|---------------------|-------------|--------------------------------------------------------|
| `IsAny`             | `is_any`    | Always passes (`True`). Represents `typing.Any`.       |
| `IsTyping`          | `is_typing` | Recursively converts an annotation into a `Rule` tree. |
| `build_typing_rule` | -           | Functional entry point for annotation decomposition.   |

➡️ [README_RULE_TYPING](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_TYPING.md)

➡️ [README_RULE_TYPING_BUILDERS](https://github.com/simplibs/simplibs-rules/blob/main/docs/rules/README_RULE_TYPING_BUILDERS.md)

---

## 🧪 Testing Utilities

`simplibs-rules` includes its own contract testing tools to ensure custom or existing `Rule` 
implementations strictly follow all rules and return modes:

* **`assert_rule_contract`**: Verifies `is_valid`, direct calling, `validate()` matrix, 
  return modes, exception generation, and `raise_invalid()` consistency for any `Rule` instance.

➡️ [README_TESTING_ASSERTS_RULE_CONTRACT](https://github.com/simplibs/simplibs-rules/blob/main/docs/testing/README_TESTING_ASSERTS_RULE_CONTRACT.md)

---

---

## ☯️ About simplibs

All libraries in the **simplibs** (Simple Libraries) ecosystem share a common
engineering philosophy:

* **Dyslexia-friendly:**
We actively minimize cognitive load. Code is atomized into small, self-contained units,
files are named directly after the logical task they perform, and explanations describe
*why* something is designed, not just *what* it is.
* **Programmer's Zen:**
Nothing should be missing, and nothing should be superfluous. We value clean execution
paths and robust, understandable code architectures over rushed, messy feature sets.
* **Defensive Style:**
We actively anticipate edge cases and failure modes so that only safe operational paths
remain. Our code is built to degrade gracefully rather than crash unexpectedly.
* **Minimalism:**
Find the most direct path to the goal in as few operational steps as possible without
taking shortcuts on safety, readability, or completeness.
* **Code as Craft:**
Code should be pleasant to look at, readable at a glance, and evoke structural harmony.
We treat software engineering as a precision trade.

---

### 🤝 Contributing & Community

This is an **open-source project** built with love and care. We strongly believe in
community collaboration and welcome any feedback, bug reports, or feature ideas!

* **Want to contribute?** Feel free to open an Issue or submit a Pull Request.
* **Want to get in touch?** If you'd like to discuss the project further, collaborate,
  or just say hello, feel free to open a GitHub Issue or start a Discussion.

---

### 📝 License

This library is released under the **MIT License**. Build great things!

---

---

[▲ Back to Top](#-simplibs-rules)
