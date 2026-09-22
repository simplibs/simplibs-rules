from .raise_container_param_not_type_error import raise_container_param_not_type_error
from .raise_requires_at_least_one_rule_error import raise_requires_at_least_one_rule_error
from .raise_rule_param_not_callable import raise_rule_param_not_callable
from .validate_compose_param_is_callable import validate_compose_param_is_callable


_DESIGN_NOTES = """
# Container Rules Constructor Validators Sub-Package

## Purpose
Guard functions used by container rule constructors (`__init__`) to
fail-fast on invalid configuration, raising structured `ValidationError` or
`ParamError` diagnostics before an invalid rule instance can be created.

## Internal Components Registry

| Component                                | Type     | Description                                                                 |
| :----------------------------------------- | :------- | :----------------------------------------------------------------------------|
| `raise_container_param_not_type_error`      | Function | Raises when a constructor parameter does not have the expected type.       |
| `raise_requires_at_least_one_rule_error`    | Function | Raises when a variadic container was initialized without any rules.        |
| `raise_rule_param_not_callable`             | Function | Raises when a single-rule container (`ForEach`, `Not`) got a non-callable. |
| `validate_compose_param_is_callable`        | Function | Validates `Compose`'s `transformer`/`validator` parameters are callable.   |
"""