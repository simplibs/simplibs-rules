from typing import Any, Callable
# Outers
from ...base_class import Rule
from simplibs.exception import ValidationError
from .._helpers import accepts_one_positional_argument
from .._init_validators import (
    raise_user_rule_param_wrong_arity,
    raise_param_not_callable_error
)


class UserRule(Rule):
    """Wrap an arbitrary user-supplied callable predicate as a Rule.

    Rule:
        bool(rule(value))

    Example:
        validate(value, UserRule(lambda v: v.startswith("user_")))
    """

    __slots__ = ("rule",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, rule: Callable[[Any], bool]) -> None:

        # 1. Parameter validation
        if not callable(rule):
            raise_param_not_callable_error("UserRule", "rule", rule)

        # 2. Soft arity check — catches the unambiguous zero-argument case
        if not accepts_one_positional_argument(rule):
            raise_user_rule_param_wrong_arity("UserRule", rule)

        # 3. Parameter assignment
        self.rule = rule

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    # noinspection PyBroadException
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate the wrapped callable — any exception it raises
        #    counts as validation failure, never propagates
        try:
            return bool(self.rule(value))
        except Exception:
            return False

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Prepare data
        rule_name = getattr(self.rule, "__name__", repr(self.rule))

        # 2. Build the exception
        return ValidationError(
            error_name="USER_RULE_ERROR",
            label=value_name,
            expected=f"value satisfying callable condition '{rule_name}'",
            value=value,
            problem=f"Value failed (or raised inside) callable '{rule_name}'.",
            context=context,
            how_to_fix=(f"Provide a value accepted by '{rule_name}'.",),
            exception=ValueError,
        )


_DESIGN_NOTES = """
# UserRule — Arbitrary Callable Predicate Wrapper

## Purpose
Wraps any user-supplied callable (a lambda, a named function, a bound
method) as a Rule — the "escape hatch" letting an arbitrary one-off
predicate participate in the same |/&/~ composition, Annotated metadata,
and diagnostic pipeline as every purpose-built predicate class.

---

## 1. `is_valid` Never Propagates the Wrapped Callable's Exceptions

An exception raised inside `self.rule(value)` is caught and treated as
validation failure (`False`), never re-raised — preserving the same
contract every Rule in this library upholds for a callable this library
did not write and cannot vouch for. `build_exception` does not re-invoke
`self.rule(value)` to distinguish "returned False" from "raised" — both
produce the same diagnostic card; the distinction was not judged
valuable enough to justify calling a possibly-side-effecting user
callable a second time just to build an error message.

---

## 2. Arity Checking Delegated to accepts_one_positional_argument

Kept as a standalone helper (rules/predicates/logic/_helpers/) rather
than inlined here — see its own design notes for the soft, permissive
rationale this class relies on.

---

## 3. Naming: `UserRule`, Not `LambdaRule`/`IsLambda`

Kept general-purpose rather than lambda-specific: this class wraps any
callable, not only literal `lambda` expressions. `IsLambda` was also
rejected — it reads as "is this value a lambda", the opposite of what
this class actually checks (whether a value *satisfies* the given
callable).
"""