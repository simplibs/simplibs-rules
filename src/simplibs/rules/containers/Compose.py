from typing import Any, Callable
from simplibs.exception import ValidationError
# Outers
from ..base_class import Rule
# Inners
from ._helpers import as_predicate, build_child_exception, describe_rule
from ._init_validators import validate_compose_param_is_callable


class Compose(Rule):
    """Transform the value, then validate the transformed result.

    Rule:
        rule(transformer(value))

    Example:
        validate(value, Compose(str.strip, HasLength(min_=1)))
    """

    __slots__ = ("transformer", "validator")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(
        self,
        transformer: Callable[[Any], Any],
        validator: Rule | Callable[[Any], bool],
    ) -> None:

        # 1. Parameter validation
        if not (callable(transformer) and callable(validator)):
            validate_compose_param_is_callable("transformer", transformer)
            validate_compose_param_is_callable("validator", validator)

        # 2. Parameter assignment
        self.transformer = transformer
        self.validator = validator

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Transform the value
        try:
            transformed = self.transformer(value)
        except Exception:
            return False

        # 2. Evaluate the rule on the transformed value
        return as_predicate(self.validator)(transformed)

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Attempt the transformation and catch any transformation error
        try:
            transformed = self.transformer(value)
        except Exception as transform_error:
            transformer_name = describe_rule(self.transformer)
            return ValidationError(
                error_name="COMPOSE_TRANSFORM_FAILED_ERROR",
                label=value_name,
                expected=f"value compatible with transformer '{transformer_name}'",
                value=value,
                problem=(
                    f"Transformation by '{transformer_name}' failed with "
                    f"{type(transform_error).__name__}: {transform_error}"
                ),
                context=context,
                how_to_fix=(
                    f"Provide a value that can be transformed by '{transformer_name}'.",
                ),
                exception=TypeError,
            )

        # 2. Evaluate the validator on the transformed value
        if not as_predicate(self.validator)(transformed):
            return build_child_exception(
                self.validator,
                transformed,
                value_name,
                context,
            )

        # 3. Fallback (build exception if both transformation and validation
        #    unexpectedly passed)
        return ValidationError(
            error_name="COMPOSE_UNREACHABLE_ERROR",
            label=value_name,
            expected="value passing both transformation and validation",
            value=value,
            problem="Transformation and validation unexpectedly passed during error construction.",
            context=context,
            how_to_fix=("Check transformer or validator logic state.",),
            exception=RuntimeError,
        )


_DESIGN_NOTES = """
# Compose — Value Transformation & Sequential Validation Rule

## Purpose
The `Compose` rule applies a transformation callable to an input value and
subsequently validates the transformed output against a target rule or
predicate.

---

## 1. Execution Rationale & Inline Error Handling

* **Stateless Design & Thread Safety:**
  Avoids mutating `self` during evaluation. Instances of `Compose` are fully
  stateless, immutable, and safe to share across concurrent threads or
  reuse globally.
* **Execution Replay in Error Path:**
  `build_exception` replays the transformation steps on failure to maintain
  statelessness.
* **Inline Transformation Diagnostics:**
  Directly constructs `COMPOSE_TRANSFORM_FAILED_ERROR` within
  `build_exception` when `self.transformer(value)` raises an exception,
  safely retrieving function signatures via `describe_rule`.
* **Validation Failure Delegation:**
  Passes the successfully transformed output to `build_child_exception` for
  sub-rule error construction.

---

## 2. Exception Card Design

* **Transformed Value Diagnostics:**
  Validation failure exceptions directly report on `transformed` rather
  than raw `value`, ensuring accurate feedback for the user.
* **Transformation Fault Classification:**
  Transformation failures raise a `TypeError` wrapper containing the
  original exception class name and message directly in the `problem`
  field.
"""
