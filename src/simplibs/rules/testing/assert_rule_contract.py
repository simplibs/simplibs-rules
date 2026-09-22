from typing import Any, Callable
# Outers
from ..base_class import Rule
# Inners
from .asserts.assert_rule_is_valid import assert_rule_is_valid
from .asserts.assert_rule_validate import assert_rule_validate
from .asserts.assert_rule_build_exception import assert_rule_build_exception
from .asserts.assert_rule_param_error import assert_rule_param_error
from .asserts.assert_rule_raise_invalid import assert_rule_raise_invalid


def assert_rule_contract(
    subtests: Any,
    rule: Rule,
    valid_values: list[Any],
    invalid_values: list[Any],
    *,
    expected_error_name: str | None = None,
    expected_exception_type: type[Exception] | None = None,
    rule_factory: Callable[..., Any] | None = None,
    invalid_init_params: list[tuple[tuple[Any, ...], dict[str, Any]]] | None = None,
    sample_label: str = "target_var",
    sample_context: str = "test_execution_context",
    check_value: bool = True,
    check_raise_invalid: bool = False,
    verbose: bool = True,
    intro: str = "",
    deep_check: bool = True,
) -> None:
    """Master orchestrator for testing rule compliance against the simplibs-validate contract.

    Runs the full battery of deterministic checks a well-formed `Rule` subclass must
    satisfy: the `is_valid()`/`__call__` boolean contract, the `validate()` mode matrix,
    the `build_exception()` diagnostic card contract, and — optionally — the constructor's
    `ParamError` guard and the standalone `raise_invalid()` dispatcher.

    Everything checked here is deterministic given valid_values/invalid_values, so a single
    call replaces most of what a hand-written test module for a Rule subclass would need.
    Anything rule-specific beyond this (e.g. asserting exact `problem`/`how_to_fix` wording
    for one particular invalid value) is expected to be written as an additional, focused
    test alongside this call — not folded into the generic contract.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        rule: The Rule instance under test.
        valid_values: Values that must satisfy the rule.
        invalid_values: Values that must fail the rule and produce a diagnostic exception.
        expected_error_name: If provided, asserted against every raised exception's error_name.
        expected_exception_type: If provided, asserted against every raised exception's
            wrapped `exception` attribute.
        rule_factory: The rule class (or a factory callable) used to test constructor
            guards. Required, together with invalid_init_params, to run the constructor
            ParamError check.
        invalid_init_params: A list of (args, kwargs) pairs expected to raise ParamError
            when passed to rule_factory. Required, together with rule_factory, to run the
            constructor ParamError check.
        sample_label: The value_name used when probing build_exception()/raise_invalid().
        sample_context: The context used when probing build_exception().
        check_value: If True, asserts that exc.value strictly matches the raw invalid value.
            Set to False for rules that modify/transform values before failure (e.g. Compose).
        check_raise_invalid: If True, additionally verifies the standalone raise_invalid()
            function against this rule.
        verbose: If True, registers individual checks as isolated pytest subtests.
        intro: Optional prefix string added to the generated subtest identity name.
        deep_check: If True, triggers exhaustive diagnostic field inspection in the
            build_exception and constructor checks.
    """
    assert isinstance(rule, Rule), (
        f"assert_rule_contract expects a Rule instance, got {type(rule).__name__}."
    )

    rule_name = type(rule).__name__
    prefix = f"{intro}[{rule_name}] " if intro == "" else f"{intro} "

    # 1. Test is_valid() and __call__()
    assert_rule_is_valid(
        subtests,
        rule,
        valid_values,
        invalid_values,
        verbose=verbose,
        intro=prefix,
    )

    # 2. Test validate() modes
    assert_rule_validate(
        subtests,
        rule,
        valid_values,
        invalid_values,
        verbose=verbose,
        intro=prefix,
    )

    # 3. Test build_exception()
    assert_rule_build_exception(
        subtests,
        rule,
        invalid_values,
        expected_error_name=expected_error_name,
        expected_exception_type=expected_exception_type,
        sample_label=sample_label,
        sample_context=sample_context,
        check_value=check_value,
        deep_check=deep_check,
        verbose=verbose,
        intro=prefix,
    )

    # 4. Optional: standalone raise_invalid() dispatcher
    if check_raise_invalid:
        assert_rule_raise_invalid(
            subtests,
            rule,
            invalid_values,
            verbose=verbose,
            intro=prefix,
        )

    # 5. Optional constructor ParamError check
    if deep_check and invalid_init_params and rule_factory:
        assert_rule_param_error(
            subtests,
            rule_factory,
            invalid_init_params,
            verbose=verbose,
            intro=prefix,
        )


_DESIGN_NOTES = """
# assert_rule_contract (Master Rule Compliance Orchestrator)

## Purpose
The single entry point for testing any `simplibs-validate` `Rule` subclass.
Mirrors the Facade pattern used by `assert_exception_function` /
`assert_exception_class` in `simplibs-exception`: one call, fed with data
(valid/invalid values, and optionally constructor misuse cases), exercises
every deterministic corner of the `Rule` contract.

---

## 1. Contract Coverage

1. **`is_valid` check** — `is_valid()` / `__call__` boolean contract.
2. **`validate` check** — the `validate()` mode matrix (raise / return_value / return_bool).
3. **`build_exception` check** — `build_exception()` produces a well-formed, raisable card.
   Supports `check_value=False` for transformation rules (e.g. `Compose`).
4. **`raise_invalid` check** (opt-in via `check_raise_invalid`) — the standalone
   `raise_invalid()` dispatcher agrees with `build_exception()`.
5. **constructor `ParamError` check** (opt-in via `rule_factory` +
   `invalid_init_params`) — the constructor rejects bad configuration with `ParamError`.

Steps 4 and 5 are opt-in because not every rule has constructor parameters
worth misuse-testing (e.g. `IsNone`, `IsTrue`), and `raise_invalid` is a
thin, generic dispatcher shared by every rule — most callers won't need to
re-verify it per rule.

---

## 2. Design Choices

* **Fail-Fast Type Guard:**
  Asserts `isinstance(rule, Rule)` immediately, before any check runs, so
  misuse of this helper itself produces one clear error instead of a
  cascade of confusing subtest failures.
* **No Wrapping Subtest Per Step:**
  Each delegated blade (`assert_rule_is_valid`, `assert_rule_validate`, ...)
  already opens its own per-value `maybe_subtest` blocks internally.
  `pytest-subtests` catches and records a failure at the level of the
  `subtests.test()` block where it occurs and does not propagate it back
  out — so wrapping a second, outer `maybe_subtest` around each delegated
  call here would never actually observe a failure from within it, while
  still doubling up subtest name prefixes in the report. The `prefix`
  (built from `intro` and the rule's class name) passed as `intro` into
  every delegated call is what provides the grouping/readability benefit,
  without a redundant, effectively-always-green wrapper subtest.
* **`deep_check` Scope:**
  Gates both the exhaustive diagnostic-field inspection inside
  `build_exception` checking and the optional constructor `ParamError`
  sweep — mirroring `assert_exception_function`'s own `deep_check` split
  between "smoke test" and "full compliance audit".
* **Toolkit Reuse Over Reimplementation:**
  Every delegated blade (`assert_rule_validate`, `assert_rule_build_exception`,
  `assert_rule_param_error`) is itself built on top of
  `simplibs-exception`'s own testing primitives
  (`assert_function_valid_input`, `assert_function_raises`,
  `assert_exception_function`) rather than re-implementing raise/type/field
  checking — the same category of bug fixed once in `simplibs-exception`
  benefits this library automatically.
* **Scope Boundary — What This Does NOT Do:**
  This orchestrator only checks what is fully deterministic given the
  supplied values. It does not (and should not) assert exact `problem` /
  `how_to_fix` wording for specific invalid values — that is inherently
  rule-specific and belongs in a small, focused test written alongside
  the `assert_rule_contract` call, not folded into the generic contract
  itself.
"""