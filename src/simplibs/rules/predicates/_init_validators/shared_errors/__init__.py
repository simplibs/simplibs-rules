from .raise_param_min_max_bounds_inverted_error import raise_param_min_max_bounds_inverted_error
from .raise_param_min_max_incomparable_error import raise_param_min_max_incomparable_error
from .raise_param_missing_error import raise_param_missing_error
from .raise_param_not_callable_error import raise_param_not_callable_error
from .raise_param_not_container_error import raise_param_not_container_error
from .raise_param_not_non_negative_integer_error import raise_param_not_non_negative_integer_error
from .raise_param_not_string_error import raise_param_not_string_error
from .raise_param_not_type_error import raise_param_not_type_error


_DESIGN_NOTES = """
# Shared Constructor Error Guards Sub-Package

## Purpose
Generic, unconditional `ParamError`-raising helpers reused across many
predicate rule constructors. Each helper is driven by an internal
`_PARAM_CONFIG` mapping that supplies rule- and parameter-specific
diagnostic text, keeping the raising logic itself rule-agnostic.

## Internal Components Registry

| Component                                        | Type     | Description                                                            |
| :----------------------------------------------- | :------- | :--------------------------------------------------------------------- |
| `raise_param_min_max_bounds_inverted_error`      | Function | Raises when a range's minimum boundary exceeds its maximum.            |
| `raise_param_min_max_incomparable_error`         | Function | Raises when a range's boundaries have incomparable types.              |
| `raise_param_missing_error`                      | Function | Raises when a rule was constructed without any required constraint.    |
| `raise_param_not_callable_error`                 | Function | Raises when a parameter is not a callable object (function, lambda...).|
| `raise_param_not_container_error`                | Function | Raises when a parameter is not a container (list, set, tuple, ...).    |
| `raise_param_not_non_negative_integer_error`     | Function | Raises when a parameter is not a non-negative integer.                 |
| `raise_param_not_string_error`                   | Function | Raises when a parameter is not a string.                               |
| `raise_param_not_type_error`                     | Function | Raises when a parameter is not a class type (`type`) object.           |
"""