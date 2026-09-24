# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.2.2] - 2026-09-24

### 📋 Improved

#### Testing Utils (`simplibs.rules.testing`)

* **Enhanced Contract Assertions for `Sequence` Inputs**:
  * Updated `assert_rule_build_exception` and `assert_rule_contract` to accept index-matched `Sequence` instances (or `Sequence[... | None]`) for both `expected_error_name` and `expected_exception_type`.
  * Enables testing compound rules (such as `AllOf` or `AnyOf`) where different invalid inputs trigger distinct sub-rule error names or exception types.
  * Added runtime sequence length validation with early fail-fast `ValueError` checks to prevent confusing `IndexError` exceptions.
  * Explicitly guarded `str` and `type` objects from being misinterpreted as sequences during parameter resolution.

---

## [0.2.1] - 2026-09-24

### ✨ Added

#### Predicate Rules (`simplibs.rules.predicates.strings`)

* **`IsIdentifier`**: Rule validating whether a string is a valid Python identifier (matching `str.isidentifier()`). Includes `is_identifier` shortcut and namespace exports.
* **`IsPrintable`**: Rule validating whether a string contains only printable characters or is empty (matching `str.isprintable()`). Includes `is_printable` shortcut and namespace exports.
* **`IsWhitespace`**: Rule validating whether a string consists entirely of whitespace characters and is non-empty (matching `str.isspace()`). Includes `is_whitespace` shortcut and namespace exports.

---

## [0.2.0] - 2026-09-23

### 🗑️ Removed & Breaking Changes

* **`raise_invalid` tool (`simplibs.rules.tools.raise_invalid`)**:
  * Moved to the `simplibs-validate` package
    (`simplibs.validate.tools.raise_invalid`).
  * **Reason for change:** Maintaining conceptual purity of the `simplibs-rules`
    package. The `RULES` library strictly serves as a declarative logic module
    focused on defining, composing, and evaluating conditions (`Rule`, predicates,
    and boolean logic). Executing validation responses, code enforcement, and
    direct exception raising belongs in the `simplibs-validate` execution layer.

* **Testing Utils (`simplibs.rules.testing`)**:
  * Removed support for `raise_invalid` from testing tools (removed the
    `assert_rule_raise_invalid` helper and the `check_raise_invalid` parameter
    from the `assert_rule_contract` orchestrator).
  * **Reason for change:** Testing tools in `simplibs-rules` now focus exclusively
    on verifying the `Rule` class contract (`is_valid`, `validate`,
    `build_exception`, `ParamError`). Testing for `raise_invalid` will be available in
    the `simplibs-validate` package.

---

## [0.1.0] - 2026-09-22

### ✨ Added

#### `Rule` — Base Class (`simplibs.rules.base_class`)

* Abstract `is_valid(value)` / `build_exception(value, value_name, context)`
  contract every rule implements
* `validate(...)` — full return-mode interface (`raise` / `True`/`False` /
  value)
* `__call__` — predicate shorthand (`rule(value)`)
* Operator-based composition: `|` (`AnyOf`), `&` (`AllOf`), `~` (`Not`),
  including reflected (`__ror__`/`__rand__`) support for plain callables
  on the left-hand side
* `annotated(type_)` — bridges any `Rule` directly into
  `typing.Annotated[type_, self]`
* `_NotARule` internal wrapper for non-rule fallbacks and legacy predicate
  wrapping

#### Container Rules (`simplibs.rules.containers`)

* `AllOf`, `AnyOf`, `NoneOf` — variadic composition (all/any/none of the
  given rules), with automatic flattening of same-type nested instances
  from operator chaining
* `Not` — single-rule negation
* `ForEach` — per-item validation over an iterable, with per-index failure
  diagnostics
* `Compose` — transform-then-validate, for normalize-before-check patterns

#### Predicate Rules (`simplibs.rules.predicates`)

* **Arithmetic**: `CloseTo`, `DivisibleBy`, `HasRemainder`
* **Checkers**: `IsNone`, `IsTrue`, `IsFalse` (identity-based), `IsEmpty`,
  `NotEmpty`
* **Collections**: `AllUnique`, `HasItem`, `HasKey`, `HasKeys`,
  `IsContainer`, `IsSubsetOf`, `IsSupersetOf`
* **Comparisons**: `Equals`, `NotEquals`, `GreaterThan`, `GreaterOrEqual`,
  `LessThan`, `LessOrEqual`, `InRange` (configurable bound inclusivity)
* **Introspection**: `IsInstance`, `IsType`, `IsSubclass`, `IsDataclass`,
  `IsCallable`, `IsHashable`, `IsIterable`, `HasAttribute`, `HasLength`
* **Logic**: `Is`, `IsNot` (identity), `IsIn`, `NotIn` (membership, with
  optional `strict` type-exact matching), `UserRule` (wraps an arbitrary
  callable predicate, with constructor-time arity validation)
* **Numeric**: `IsBool`, `IsInteger`, `IsFloat`, `IsDecimal`, `IsNumber`,
  `IsPrimitiveNumber`, `IsZero`, `IsNan`, `IsInfinity`, `IsPi` — booleans
  consistently excluded from every "real number" check
* **Strings**: `IsString`, `Contains`, `IsSubstringOf`, `StartsWith`,
  `EndsWith`, `Regex`, `IsBlank`, `NotBlank`

#### Snake-Case Shortcuts & Namespaces

* Pre-instantiated or class-level snake_case shortcuts for every built-in
  rule (e.g. `is_integer`, `greater_than`, `regex`), fully interchangeable
  with and composable alongside the class form

#### Operational Helpers (`simplibs.rules.tools`)

* `raise_invalid(value, rule, *, value_name=None, context=None)` — direct
  exception-raising helper that bypasses rule evaluation when application
  control flow guards have already detected an inline failure condition
  (relocated here from `simplibs-validate` during testing, once it became
  clear it only ever needs a `Rule`/callable and a value — no dependency
  on anything `simplibs-validate` adds on top)

#### Annotation-Driven Rules (`simplibs.rules.predicates.typing`)

* `IsTyping(annotation)` — recursively decomposes an arbitrary type
  annotation into a composed `Rule` tree, built once at construction
* `build_typing_rule(annotation)` — recursive dispatcher underlying `IsTyping`
* `IsAny` — structural counterpart to `typing.Any` within the decomposition
  tree
* Dispatch table (`ORIGIN_TABLE`) and a family of per-process builders
  covering: element collections (`list`/`set`/`frozenset`/`Iterable`/
  `Sequence`/`Collection`), key-value mappings (`dict`/`Mapping`/
  `MutableMapping`), homogeneous and fixed-length tuples, unions
  (`Union`/`X | Y`, including `Optional`), `Literal` (with strict
  type-exact matching), `Type`/`type` (including `Union` and `Any` bases),
  `Callable`, and `Annotated` metadata unpacking
* Support for both modern (`collections.abc`) and legacy (`typing.List`,
  `typing.Dict`, ...) annotation spellings

#### Testing Utilities (`simplibs.rules.testing`)

* `assert_rule_contract` — master facade running the full deterministic
  `Rule` contract battery: `is_valid`/`__call__`, the `validate()` return-mode
  matrix, `build_exception()`'s diagnostic-card contract, plus optional
  constructor validation and consistency checks

#### Documentation

* Full reference documentation for the `Rule` base class, container rules,
  atomic predicate packages, typing decomposition engine, and contract
  testing utilities
* Complete rule quick-reference tables in the main README

#### Dependencies

* `simplibs-exception` — structured exception framework underlying rule
  failure diagnostics
* `simplibs-sentinels` — sentinel values (`UNSET`) for distinguishing unset
  arguments from `None`

---

## Legend

* 🔄 **Changed** — modifications to existing functionality
* ✨ **Added** — new features and components
* 🐛 **Fixed** — bug fixes
* 📋 **Improved** — enhancements to existing features
* ⚠️ **Deprecated** — deprecated functionality (not used yet in this project)
* 🗑️ **Removed** — removed functionality (not used yet in this project)