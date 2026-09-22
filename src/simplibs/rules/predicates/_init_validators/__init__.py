from .rule_errors import (
    raise_has_length_param_conflict_error,
    raise_regex_param_invalid_pattern_error,
    raise_user_rule_param_wrong_arity,
)
from .shared_errors import (
    raise_param_min_max_bounds_inverted_error,
    raise_param_min_max_incomparable_error,
    raise_param_missing_error,
    raise_param_not_container_error,
    raise_param_not_non_negative_integer_error,
    raise_param_not_string_error,
    raise_param_not_type_error,
    raise_param_not_callable_error,
)
from .shared_validators import (
    validate_param_is_integer,
    validate_param_is_not_zero,
    validate_param_is_primitive_number,
    validate_param_remainder_in_range,
)


_DESIGN_NOTES = """
# Predicate Rules Constructor Validators Sub-Package

## Purpose
Groups every constructor-time guard used by predicate rules (as opposed to
container rules) under one namespace, split into three sub-packages by
scope: rule-specific error guards, shared error guards, and shared
happy-path validators.

## Internal Sub-Package Registry

| Sub-Package          | Description                                                                      |
| :--------------------- | :----------------------------------------------------------------------------------|
| `rule_errors`          | `ParamError` guards tailored to a single specific rule (`HasLength`, `Regex`).   |
| `shared_errors`        | Generic, unconditional `ParamError` guards reused across many rules.            |
| `shared_validators`    | Generic, happy-path-first checks that delegate to `shared_errors` on failure.   |
"""
