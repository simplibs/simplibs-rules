from .AllOf import AllOf
from .AnyOf import AnyOf
from .Compose import Compose
from .ForEach import ForEach
from .NoneOf import NoneOf
from .Not import Not


_DESIGN_NOTES = """
# Container Validation Rules Sub-Package

## Purpose
Composite rules that combine, transform, or otherwise operate on other
rules or callables rather than validating a value directly. These form the
logical/structural layer of the rule system, built on top of the individual
predicate rules.

## Internal Components Registry

| Component | Type  | Description                                                                     |
| :-------- | :---- | :--------------------------------------------------------------------------------|
| `AllOf`    | Class | Value must satisfy every given rule (logical AND).                              |
| `AnyOf`    | Class | Value must satisfy at least one given rule (logical OR).                        |
| `NoneOf`   | Class | Value must satisfy none of the given rules.                                     |
| `Not`      | Class | Inverts the result of a single wrapped rule or predicate.                       |
| `ForEach`  | Class | Applies a rule to every item in an iterable value.                              |
| `Compose`  | Class | Transforms the value, then validates the transformed result.                    |
"""