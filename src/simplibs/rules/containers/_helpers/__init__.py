from .as_predicate import as_predicate
from .build_child_exception import build_child_exception
from .describe_rule import describe_rule


_DESIGN_NOTES = """
# Container Rules Internal Helpers Sub-Package

## Purpose
Shared runtime helpers used internally by container rules (`AllOf`, `AnyOf`,
`NoneOf`, `Not`, `ForEach`, `Compose`) to normalize child rules into
predicates, delegate exception construction, and produce readable rule
descriptions for diagnostic messages.

## Internal Components Registry

| Component               | Type     | Description                                                                     |
| :----------------------- | :------- | :--------------------------------------------------------------------------------|
| `as_predicate`            | Function | Normalizes a `Rule` instance or callable into a plain `Callable[[Any], bool]`.  |
| `build_child_exception`   | Function | Delegates exception construction to a child `Rule` or a callable fallback.      |
| `describe_rule`           | Function | Returns a readable name for a rule or callable, for use in error messages.      |
"""