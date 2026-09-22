from .validate_param_is_integer import validate_param_is_integer
from .validate_param_is_not_zero import validate_param_is_not_zero
from .validate_param_is_primitive_number import validate_param_is_primitive_number
from .validate_param_remainder_in_range import validate_param_remainder_in_range


_DESIGN_NOTES = """
# Shared Constructor Value Validators Sub-Package

## Purpose
Generic, happy-path-first constructor guards reused across many predicate
rules. Unlike `shared_errors`, each validator first checks the condition
itself and only delegates to a `ParamError` (typically from `shared_errors`)
when the check fails, rather than raising unconditionally.

## Internal Components Registry

| Component                             | Type     | Description                                                                 |
| :---------------------------------------| :------- | :---------------------------------------------------------------------------|
| `validate_param_is_integer`             | Function | Checks that a parameter is strictly an `int` (booleans excluded).           |
| `validate_param_is_not_zero`            | Function | Checks that a numeric parameter (e.g., a divisor) is not zero.              |
| `validate_param_is_primitive_number`    | Function | Checks that a parameter is a primitive `int`/`float` (booleans excluded).   |
| `validate_param_remainder_in_range`     | Function | Checks that a remainder satisfies `0 <= remainder < |divisor|`.             |
"""
