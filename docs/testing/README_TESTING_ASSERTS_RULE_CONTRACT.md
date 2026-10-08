# 🧪 `assert_rule_contract`

**Comprehensive `Rule` Subclass Compliance Audit**

`assert_rule_contract` is the master facade for testing any `Rule` subclass in
`simplibs-rules`. It unifies six granular, isolated compliance checks into a
single, predictable, sequential verification pipeline — everything a well-formed rule
must satisfy, given nothing more than a list of values that must pass and a list that
must fail.

## 💡 Table of Contents:
> * [⚙️ Architectural Principles](#-architectural-principles)
> * [🧭 Pipeline Execution Flow](#-pipeline-execution-flow)
> * [🔍 Quick Usage Examples](#-quick-usage-examples)
> * [🛠️ Configuration & Parameters](#-configuration--parameters)
> * [🔄 Audit Pipeline (6 Checks)](#-audit-pipeline-6-checks)
>   * [Check 1: `is_valid()` / `__call__` Boolean Contract](#check-1-is_valid--__call__-boolean-contract)
>   * [Check 2: `validate()` Return-Mode Matrix](#check-2-validate-return-mode-matrix)
>   * [Check 3: `build_exception()` Diagnostic Card Contract](#check-3-build_exception-diagnostic-card-contract)
>   * [Check 4: `describe()` Text Contract](#check-4-describe-text-contract)
>   * [Check 5: `__slots__` Integrity](#check-5-__slots__-integrity)
>   * [Check 6: Constructor `ParamError` Guard (Optional)](#check-6-constructor-paramerror-guard-optional)
> * [📖 Real-World Examples](#-real-world-examples)
> * [📊 Terminal Output Comparison](#-terminal-output-comparison)

[⬅️ Back to main README](../../README.md#-testing-utilities)

---

## ⚙️ Architectural Principles

* **Facade Pattern:** Orchestrates six independent, focused assertions through a
  single master call — the primary, everyday way this library's own test suite
  verifies a rule, and the recommended way to test any custom `Rule` subclass built on
  top of it.
* **Fully Deterministic Given Its Inputs:** Every check here follows mechanically from
  `valid_values`/`invalid_values` — it never needs to know anything rule-specific
  about *why* a value is valid or invalid. This is also its boundary: it cannot verify
  the exact wording of one particular `problem`/`how_to_fix` message. Tests needing
  that level of specificity are written alongside a call to this function, not instead
  of it. The one exact text it *can* pin is the rule's description, when the caller
  supplies `expected_description`.
* **Fail-Fast for Rule-Level Mistakes:** The structural checks (`describe()` contract,
  `__slots__` integrity, constructor `ParamError` guards) exist because a rule that
  returns an empty description, silently keeps a per-instance `__dict__`, or has a
  broken constructor guard is a bug just as real as bad validation logic — but one
  that wouldn't otherwise be caught by exercising `is_valid`/`validate` alone.
* **Auto-Prefixed Diagnostics:** Every generated subtest name is automatically
  prefixed with the rule's own class name, unless a custom `intro` is supplied — so a
  failure reported anywhere in a large test suite is traceable back to the specific
  rule that produced it at a glance.

[▲ Back to Top](#-assert_rule_contract)

---

## 🧭 Pipeline Execution Flow

The orchestrator runs its checks in a fixed order, four of them always, one by default
(and switchable off), one only when the relevant arguments are supplied:

1. **Boolean Contract** (`is_valid()` / `__call__`) — always runs.
2. **Validate Return-Mode Matrix** (`validate()`) — always runs.
3. **Diagnostic Card Contract** (`build_exception()`) — always runs.
4. **Description Contract** (`describe()`) — always runs. The exact text is compared
   only if `expected_description` is given.
5. **Slots Integrity** (`__slots__`) — runs unless `check_slots=False`.
6. **Constructor `ParamError` Guard** — only if `deep_check=True` **and** both
   `rule_factory` and `invalid_init_params` are given.

[▲ Back to Top](#-assert_rule_contract)

---

## 🔍 Quick Usage Examples

```python
# 1. Standard comprehensive rule audit
assert_rule_contract(
    subtests,
    rule=GreaterThan(0),
    valid_values=[1, 100],
    invalid_values=[0, -1, "not a number"],
)

# 2. With expected diagnostic identity checks
assert_rule_contract(
    subtests,
    rule=IsInteger(),
    valid_values=[1, -5, 0],
    invalid_values=["1", 1.0, True],
    expected_error_name="IS_INTEGER_ERROR",
    expected_exception_type=TypeError,
)

# 3. Pinning the exact description text
assert_rule_contract(
    subtests,
    rule=IsInstance(int) | IsNone(),
    valid_values=[1, None],
    invalid_values=["1", 1.5],
    expected_description="int | None",
)

# 4. Including the constructor ParamError guard
assert_rule_contract(
    subtests,
    rule=AllOf(IsInteger(), GreaterThan(0)),
    valid_values=[1, 10, 100],
    invalid_values=[-5, 0, "string", None],
    rule_factory=AllOf,
    invalid_init_params=[((), {})],   # AllOf() with no arguments
)

# 5. Silent mode execution without allocating pytest subtest frames
assert_rule_contract(subtests, rule=IsString(), valid_values=["a"], invalid_values=[1], verbose=False)
```

[▲ Back to Top](#-assert_rule_contract)

---

## 🛠️ Configuration & Parameters

### Mandatory Parameters

* **`subtests`** (`Any`): The native pytest subtests fixture manager instance.
* **`rule`** (`Rule`): The rule instance under test.
* **`valid_values`** (`list[Any]`): Values that must satisfy the rule.
* **`invalid_values`** (`list[Any]`): Values that must fail the rule and produce a
  diagnostic exception.

### Optional Parameters

* **`expected_error_name`** (`str | Sequence[str | None] | None`):
  Default: `None`.
  If given, asserted against every raised exception's `error_name`. A single string
  applies to every invalid value; a sequence must be exactly as long as
  `invalid_values` and is matched by index (a `None` entry skips that value). The
  sequence form is meant for compound rules such as `AllOf`/`AnyOf`, where different
  invalid values fail on different sub-rules.
* **`expected_exception_type`** (`type[Exception] | Sequence[type[Exception] | None] | None`):
  Default: `None`.
  If given, asserted against every raised exception's wrapped `exception` attribute.
  Same scalar-or-sequence behavior as `expected_error_name`.
* **`expected_description`** (`str | None`):
  Default: `None`.
  If given, `rule.describe()` must equal this text exactly. Without it, only the
  generic contract is checked (non-empty `str`, never raises).
* **`check_slots`** (`bool`):
  Default: `True`.
  The rule instance must have no `__dict__`. Set to `False` only for a rule that
  deliberately keeps one.
* **`rule_factory`** (`Callable[..., Any] | None`):
  Default: `None`.
  The rule class/factory used for the constructor `ParamError` check. Required
  together with `invalid_init_params` to run Check 6.
* **`invalid_init_params`** (`list[tuple[tuple[Any, ...], dict[str, Any]]] | None`):
  Default: `None`.
  `(args, kwargs)` pairs expected to raise `ParamError` when passed to `rule_factory`.
  Required together with `rule_factory`.
* **`sample_label`** (`str`):
  Default: `"target_var"`.
  The `value_name` used when probing `build_exception()`.
* **`sample_context`** (`str`):
  Default: `"test_execution_context"`.
  The `context` used when probing `build_exception()`.
* **`check_value`** (`bool`):
  Default: `True`.
  Asserts `exc.value` strictly matches the raw invalid value. Set `False` for rules
  that transform the value before reporting failure (e.g. `Compose`, which reports the
  *transformed* value).
* **`verbose`** (`bool`):
  Default: `True`.
  The master gate controlling subtest frame allocation.
* **`intro`** (`str`):
  Default: `""`.
  Optional namespace prefix prepended to generated subtest labels (auto-derived from
  the rule's class name when left empty).
* **`deep_check`** (`bool`):
  Default: `True`.
  Enables the extra `expected`/`problem`/`how_to_fix` content check in Check 3, and
  gates whether Check 6 runs at all (alongside `rule_factory`/`invalid_init_params`
  being supplied). Checks 4 and 5 are cheap and always run.

```python
# Function signature:
def assert_rule_contract(
    subtests: Any,
    rule: Rule,
    valid_values: list[Any],
    invalid_values: list[Any],
    *,
    expected_error_name: str | Sequence[str | None] | None = None,
    expected_exception_type: type[Exception] | Sequence[type[Exception] | None] | None = None,
    expected_description: str | None = None,
    check_slots: bool = True,
    rule_factory: Callable[..., Any] | None = None,
    invalid_init_params: list[tuple[tuple[Any, ...], dict[str, Any]]] | None = None,
    sample_label: str = "target_var",
    sample_context: str = "test_execution_context",
    check_value: bool = True,
    verbose: bool = True,
    intro: str = "",
    deep_check: bool = True,
) -> None:
```

[▲ Back to Top](#-assert_rule_contract)

---

## 🔄 Audit Pipeline (6 Checks)

### Check 1: `is_valid()` / `__call__` Boolean Contract

The most fundamental contract every `Rule` must uphold: `is_valid(value)` and
`rule(value)` must return the **literal** boolean `True`/`False` — not just something
truthy/falsy — for both valid and invalid input, and never raise.

```python
# Internal invocation:
assert_rule_is_valid(subtests, rule, valid_values, invalid_values, verbose=verbose, intro=prefix)

# Executed under the hood, per value:
assert rule.is_valid(val) is True    # for every val in valid_values
assert rule(val) is True
assert rule.is_valid(val) is False   # for every val in invalid_values
assert rule(val) is False
```

### Check 2: `validate()` Return-Mode Matrix

Verifies `rule.validate(...)`'s full return-mode behavior: the default mode, the
`return_value=True` mode, and the `return_bool=True` mode.

```python
# Internal invocation:
assert_rule_validate(subtests, rule, valid_values, invalid_values, verbose=verbose, intro=prefix)

# Executed under the hood:
assert rule.validate(value) is True                         # valid values
assert rule.validate(value, return_value=True) == value

# raises for invalid values (checked via assert_function_raises)
assert rule.validate(value, return_bool=True) is False       # invalid values
```

### Check 3: `build_exception()` Diagnostic Card Contract

Confirms every invalid value produces a genuinely usable diagnostic — not just *an*
exception, but one carrying the fields a caller (or `AllOf`'s own delegation) actually
relies on.

```python
# Internal invocation:
assert_rule_build_exception(
    subtests, rule, invalid_values,
    expected_error_name=expected_error_name,
    expected_exception_type=expected_exception_type,
    sample_label=sample_label, sample_context=sample_context,
    check_value=check_value, deep_check=deep_check,
    verbose=verbose, intro=prefix,
)

# Executed under the hood, per invalid value:
exc = rule.build_exception(value, value_name=sample_label, context=sample_context)
assert exc.label == sample_label
assert exc.context == sample_context
assert exc.value == value                     # unless check_value=False

# if deep_check:
assert isinstance(exc.expected, str) and len(exc.expected) > 0
assert isinstance(exc.problem, str) and len(exc.problem) > 0
assert isinstance(exc.how_to_fix, (str, tuple, list)) and len(exc.how_to_fix) > 0
```

### Check 4: `describe()` Text Contract

Confirms `rule.describe()` honors its contract: it returns a non-empty `str` and never
raises. Every rule inherits `describe()` with the class name as default, so the
generic check passes for rules that have not overridden it; it only fails for a rule
whose override is broken (empty or blank text, a non-`str` value, an exception).

The exact text is rule-specific by nature (`"> 0"`, `"int | None"`), so it is compared
only when the caller supplies `expected_description`.

```python
# Internal invocation:
assert_rule_describe(subtests, rule, expected_text=expected_description, verbose=verbose, intro=prefix)

# Executed under the hood:
text = rule.describe()
assert isinstance(text, str) and text.strip() != ""

if expected_description is not None:
    assert text == expected_description
```

### Check 5: `__slots__` Integrity

Confirms the rule instance carries no per-instance `__dict__`. Every rule declares
`__slots__`, but one class anywhere in the hierarchy that forgets it silently gives all
of its instances a `__dict__` again — nothing fails, the slots just stop saving
anything. The failure message names every class in the rule's MRO without `__slots__`,
so the missing declaration is found without a debugger.

Runs by default. Pass `check_slots=False` only for a rule that deliberately keeps a
`__dict__`.

```python
# Internal invocation:
if check_slots:
    assert_rule_slots(subtests, rule, verbose=verbose, intro=prefix)

# Executed under the hood:
assert not hasattr(rule, "__dict__")
```

### Check 6: Constructor `ParamError` Guard (Optional)

*Executed only when `deep_check=True` and both `rule_factory`/`invalid_init_params`
are given.* Confirms the rule's constructor rejects invalid initialization arguments
with `ParamError` — the fail-fast contract every rule with a non-trivial constructor
is expected to uphold.

```python
# Internal invocation:
if deep_check and invalid_init_params and rule_factory:
    assert_rule_param_error(subtests, rule_factory, invalid_init_params, verbose=verbose, intro=prefix)

# Executed under the hood, per (args, kwargs) pair:
def _call():
    rule_factory(*args, **kwargs)

# asserted to raise ParamError (checked via assert_function_raises)
```

[▲ Back to Top](#-assert_rule_contract)

---

## 📖 Real-World Examples

`simplibs-rules`' own test suite uses `assert_rule_contract` as the backbone of
every rule's test module. Three representative examples:

### A composed rule, with the constructor guard enabled

```python
"""Tests for the AllOf container rule."""

from simplibs.rules import AllOf, GreaterThan, IsInteger
from simplibs.rules.testing import assert_rule_contract


def test_all_of_contract(subtests):
    """Verify the complete contract of AllOf using the master orchestrator."""
    rule = AllOf(IsInteger(), GreaterThan(0))

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 10, 100],                # Must satisfy both rules
        invalid_values=[-5, 0, "string", None],   # Fails at least one of the rules
        rule_factory=AllOf,
        invalid_init_params=[
            ((), {}),  # AllOf() with no arguments raises ParamError
        ],
        deep_check=True,
        verbose=False,
    )
```

### A variadic rule, pinning its description

```python
"""Tests for the AnyOf container rule."""

from simplibs.rules import AnyOf, IsInstance, IsNone
from simplibs.rules.testing import assert_rule_contract


def test_any_of_contract(subtests):
    """Verify the complete contract of AnyOf using the master orchestrator."""
    rule = AnyOf(IsInstance(int), IsNone())

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[10, -5, None],               # Satisfies at least one rule
        invalid_values=["string", [1, 2], 1.5],    # Neither int nor None
        expected_description="int | None",         # Containers compose their children's text
        rule_factory=AnyOf,
        invalid_init_params=[
            ((), {}),  # AnyOf() with no arguments raises ParamError
        ],
        deep_check=True,
        verbose=False,
    )
```

### A simple, parameterized rule with no constructor guard to test

```python
"""Tests for the Is rule."""

from simplibs.rules import Is
from simplibs.rules.testing import assert_rule_contract

SENTINEL = object()


def test_is_contract(subtests):
    """Verify the complete contract of the Is rule."""
    rule = Is(SENTINEL)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[SENTINEL],
        invalid_values=[object(), "SENTINEL", 123, None, []],
        deep_check=True,
        verbose=False,
    )
```

`Is` takes no `rule_factory`/`invalid_init_params` — its constructor has no invalid
shape worth testing (any object is a valid `expected` argument), so Check 6 is simply
never triggered, and the call stays just as short as the check actually needed.

[▲ Back to Top](#-assert_rule_contract)

---

## 📊 Terminal Output Comparison

The `verbose` configuration transforms how pytest visualizes compliance steps in your
terminal, letting you swap between granular tracing and high-level summaries.

### Active Verbose Mode (`verbose=True`)

Ideal during development of a new rule — pinpoints the exact assertion step that
failed.

```text
tests/test_greater_than.py::test_greater_than_contract SUBPASSED[[GreaterThan] test_is_valid_true_#index_0]
tests/test_greater_than.py::test_greater_than_contract SUBPASSED[[GreaterThan] test_call_true_#index_0]
tests/test_greater_than.py::test_greater_than_contract SUBPASSED[[GreaterThan] test_is_valid_false_#index_0]
tests/test_greater_than.py::test_greater_than_contract SUBPASSED[[GreaterThan] test_validate_pass_#index_0_]
tests/test_greater_than.py::test_greater_than_contract SUBPASSED[[GreaterThan] test_validate_raises_#index_0_]
tests/test_greater_than.py::test_greater_than_contract SUBPASSED[[GreaterThan] test_build_exception_#index_0_]
tests/test_greater_than.py::test_greater_than_contract SUBPASSED[[GreaterThan] test_describe_returns_text]
tests/test_greater_than.py::test_greater_than_contract SUBPASSED[[GreaterThan] test_no_instance_dict]
tests/test_greater_than.py::test_greater_than_contract PASSED
```

### Silent Mode (`verbose=False`)

Ideal for standard continuous integration passes — keeps execution lines tidy and
focused, as used throughout this library's own test suite.

```text
tests/test_greater_than.py::test_greater_than_contract PASSED
```

[▲ Back to Top](#-assert_rule_contract)

---

[⬅️ Back to main README](../../README.md#-testing-utilities)
