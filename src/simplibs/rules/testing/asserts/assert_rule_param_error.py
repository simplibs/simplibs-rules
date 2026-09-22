from typing import Any, Callable
from simplibs.exception.testing import assert_function_raises
from simplibs.exception import ParamError


def assert_rule_param_error(
    subtests: Any,
    rule_factory: Callable[..., Any],
    invalid_init_params: list[tuple[tuple[Any, ...], dict[str, Any]]],
    *,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that the rule constructor raises ParamError for invalid initialization arguments.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        rule_factory: The rule class (or a factory callable) under test — called as
            `rule_factory(*args, **kwargs)` for each entry in invalid_init_params.
        invalid_init_params: A list of (args, kwargs) pairs, each expected to raise
            ParamError when passed to rule_factory.
        verbose: Enables isolated pytest subtest tracking for each checked call.
        intro: Optional prefix string added to generated subtest identity names.
    """

    def make_invalid_call(
        call_args: tuple[Any, ...],
        call_kwargs: dict[str, Any]
    ) -> Callable[[], None]:
        def _call() -> None:
            rule_factory(*call_args, **call_kwargs)
        return _call

    for index, (args, kwargs) in enumerate(invalid_init_params):
        assert_function_raises(
            subtests,
            make_invalid_call(args, kwargs),
            invalid_params=(),
            exception_type=ParamError,
            verbose=verbose,
            intro=f"{intro}test_param_error_#index_{index}_",
        )


_DESIGN_NOTES = """
# assert_rule_param_error (Constructor Guard Contract Blade)

## Purpose
Verifies that a rule's constructor rejects invalid initialization
arguments with a `ParamError`, reusing `simplibs-exception`'s
`assert_function_raises` blade instead of a hand-rolled
`pytest.raises(ParamError)` loop.

---

## 1. Execution Rationale & Toolkit Reuse

* **Closure-Based Call Binding:**
  Each `(args, kwargs)` pair is bound into a zero-argument closure
  (`make_invalid_call`) rather than passed through `assert_function_raises`'s
  own `invalid_params` unpacking. This is a deliberate choice: this
  helper's `invalid_init_params` already separates positional args and
  keyword args explicitly (mirroring how rule constructors are actually
  called, e.g. `HasLength(5, min_length=1)`), and expressing that combined
  shape through `assert_function_raises`'s `tuple | Kwargs` parameter
  would require assuming `Kwargs` supports mixed positional+keyword
  construction. Binding a closure sidesteps that assumption entirely
  while still routing the actual raise/type-check work through the
  shared toolkit.
* **No Deep Field Checking:**
  Unlike `assert_rule_build_exception`, this helper does not assert on
  `ParamError` field content (label, problem, ...), since the whole point
  of `invalid_init_params` is to sweep a variety of unrelated bad
  configurations (wrong type, missing value, conflicting parameters,
  inverted bounds, ...) in one list — their diagnostic text differs by
  nature, not just by value.
"""
