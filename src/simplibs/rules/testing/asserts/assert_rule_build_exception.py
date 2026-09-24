from typing import Any, Sequence
from simplibs.exception import ValidationError
from simplibs.exception.testing import assert_exception_function, maybe_subtest
# Outers
from ...base_class import Rule


# noinspection PyUnresolvedReferences
def assert_rule_build_exception(
    subtests: Any,
    rule: Rule,
    invalid_values: list[Any],
    *,
    expected_error_name: str | Sequence[str | None] | None = None,
    expected_exception_type: type[Exception] | Sequence[type[Exception] | None] | None = None,
    sample_label: str = "target_var",
    sample_context: str = "test_execution_context",
    check_value: bool = True,
    deep_check: bool = True,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that rule.build_exception() constructs valid, raisable ValidationError cards.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        rule: The Rule instance under test.
        invalid_values: Values expected to produce a diagnostic exception card.
        expected_error_name: If provided, asserted against exc.error_name. Can be
            a single string (applied to all values) or a sequence matching invalid_values
            by index.
        expected_exception_type: If provided, asserted against exc.exception. Can be
            a single Exception class (applied to all values) or a sequence matching
            invalid_values by index.
        sample_label: The value_name passed into build_exception() for every check.
        sample_context: The context passed into build_exception() for every check.
        check_value: If True, asserts that exc.value strictly matches the raw invalid value.
            Set to False for rules that modify/transform values before failure (e.g. Compose).
        deep_check: If True, additionally verifies exc.expected / exc.problem /
            exc.how_to_fix are non-empty diagnostic content.
        verbose: Enables isolated pytest subtest tracking for each checked value.
        intro: Optional prefix string added to generated subtest identity names.
    """

    def raising_wrapper(value: Any) -> None:
        raise rule.build_exception(value, value_name=sample_label, context=sample_context)

    for index, val in enumerate(invalid_values):
        kwargs: dict[str, Any] = dict(
            exception_type=ValidationError,
            label=sample_label,
            context=sample_context,
            verbose=verbose,
            intro=f"{intro}test_build_exception_#index_{index}_",
            # Always True here: assert_exception_function only calls
            # assert_exception_fields at all when deep_check is truthy, so this
            # must stay True regardless of this function's own `deep_check` —
            # otherwise label/value/context are never actually checked.
            # See DESIGN_NOTES for the bug this fixes.
            deep_check=True,
        )

        if check_value:
            kwargs["value"] = val

        # 1. Per-index evaluation of expected_error_name with sequence length guard
        if expected_error_name is not None:
            if isinstance(expected_error_name, Sequence) and not isinstance(expected_error_name, str):
                if len(expected_error_name) != len(invalid_values):
                    raise ValueError(
                        "expected_error_name sequence must have the same length as invalid_values."
                    )
                current_error_name = expected_error_name[index]
            else:
                current_error_name = expected_error_name

            if current_error_name is not None:
                kwargs["error_name"] = current_error_name

        # 2. Per-index evaluation of expected_exception_type with sequence length guard
        if expected_exception_type is not None:
            if (
                isinstance(expected_exception_type, Sequence)
                and not isinstance(expected_exception_type, type)
            ):
                if len(expected_exception_type) != len(invalid_values):
                    raise ValueError(
                        "expected_exception_type sequence must have the same length as invalid_values."
                    )
                current_exception_type = expected_exception_type[index]
            else:
                current_exception_type = expected_exception_type

            if current_exception_type is not None:
                kwargs["exception"] = current_exception_type

        exc = assert_exception_function(
            subtests,
            raising_wrapper,
            invalid_params=(val,),
            **kwargs,
        )

        # Diagnostic-quality checks: verify the shape of rule-specific fields
        # whose exact text is not known generically here (only assert_rule_contract's
        # caller could know it, and even then only per rule, not per value).
        # Gated on this function's own `deep_check`, independent of the always-True
        # value passed to assert_exception_function above.
        if deep_check:
            with maybe_subtest(
                subtests,
                name=f"{intro}test_build_exception_diagnostics_#index_{index}",
                verbose=verbose,
            ):
                assert isinstance(exc.expected, str) and len(exc.expected) > 0
                assert isinstance(exc.problem, str) and len(exc.problem) > 0
                assert isinstance(exc.how_to_fix, (str, tuple, list)) and len(exc.how_to_fix) > 0


_DESIGN_NOTES = """
# assert_rule_build_exception (Exception Card Contract Blade)

## Purpose
Verifies that `Rule.build_exception()` produces a well-formed, raisable
`ValidationError` diagnostic card for every invalid value — reusing
`simplibs-exception`'s own `assert_exception_function` rather than
re-implementing raise/type/field checking here.

---

## 1. Execution Rationale & Toolkit Reuse

* **Raising Wrapper:**
  `build_exception()` *returns* an exception rather than raising it (by
  contract — see `Rule`'s design notes: "the exception is only assembled
  and returned"). `assert_exception_function` expects a callable that
  *raises*, so this helper wraps the call in a small local
  `raising_wrapper(value)` that raises whatever `build_exception` returns.
* **Basic Metadata via `assert_exception_function`:**
  Delegates the type check (`ValidationError`), and the `label`/`context`/
  `value` echo-back checks, to `assert_exception_function`.
* **Flexible Expected Fields (Scalar vs Sequence):**
  `expected_error_name` and `expected_exception_type` support both single values
  (applied uniformly across all `invalid_values`) and index-matched `Sequence`s
  (for compound rules like `AllOf`/`AnyOf` where different invalid inputs trigger
  different sub-rule failures).
* **Value Echo Bypass (`check_value=False`):**
  Rules that transform values before evaluating inner bounds (such as `Compose`)
  will legitimately report the *transformed* value inside `exc.value` instead
  of the raw input `val`. `check_value=False` omits passing `value` to the
  underlying `assert_exception_function`, allowing transformation rules to pass
  the card contract check without false failures.
* **Shape-Only Diagnostic Check (`deep_check=True`):**
  Independently verifies that `expected`, `problem`, and `how_to_fix` are
  non-empty. `how_to_fix` is checked against `(str, tuple, list)` rather
  than `tuple` alone, since built-in rules use either a single string
  (`how_to_fix = "Provide ..."`) or a tuple of strings, depending on the
  rule — asserting `tuple` only would false-fail on the majority of rules
  in this library that pass a plain string.

---

## 2. Sequence Handling & Boundary Guards

* **`str` and `type` Exclusion:**
  Python's `str` implements `Sequence`, and custom exception classes (`type`)
  may occasionally match sequence protocols. The checks explicitly exclude
  `str` (`not isinstance(val, str)`) and `type` (`not isinstance(val, type)`) to
  prevent strings from being iterated as character sequences or classes from being
  misinterpreted as multi-item inputs.
* **Fail-Fast Length Validation:**
  When a sequence is provided for expected errors or types, its length must
  strictly equal `len(invalid_values)`. An early `ValueError` is raised before
  entering the subtest execution loop, avoiding confusing downstream `IndexError`
  exceptions inside individual test checkpoints.

---

## 3. Fixed Bug: deep_check Was Silently Disabling All Field Checks

An earlier revision passed `deep_check=False` straight through to the
delegated `assert_exception_function` call, tying it to this function's
own `deep_check` parameter's *false* branch. That was wrong:
`assert_exception_function` only calls `assert_exception_fields` at all
when its `deep_check` is truthy — passing `False` doesn't just skip the
"deep" fields, it skips checking `label`, `value`, and `context` too,
silently. The docstring claimed those were delegated and checked; in
practice they never ran.

Fixed by always passing `deep_check=True` to the delegated call (these are
basic metadata checks, not "deep" ones), and using this function's own
`deep_check` parameter only to gate the additional local shape-checks on
`expected`/`problem`/`how_to_fix` below — which is what it was always
meant to control.
"""