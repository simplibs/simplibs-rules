from .accepts_one_positional_argument import accepts_one_positional_argument
from .format_container import format_container

_DESIGN_NOTES = """
# Predicate Rules Internal Helpers Sub-Package

## Purpose
Shared runtime helpers used internally by predicate validation rules
(`IsSubsetOf`, `IsSupersetOf`, `IsIn`, `NotIn`, `UserRule`, etc.) to provide
consistent formatting and signature validation ahead of rule execution.

## Internal Components Registry

| Component                        | Type     | Description                                                                     |
| :------------------------------- | :------- | :------------------------------------------------------------------------------ |
| `accepts_one_positional_argument` | Function | Best-effort arity guard checking if a callable can accept `rule(value)`.        |
| `format_container`               | Function | Formats containers deterministically (sorting sets/frozensets when possible).   |
"""