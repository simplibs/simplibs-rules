from .Equals import Equals
from .NotEquals import NotEquals
from .GreaterThan import GreaterThan
from .GreaterOrEqual import GreaterOrEqual
from .LessThan import LessThan
from .LessOrEqual import LessOrEqual
from .InRange import InRange


_DESIGN_NOTES = """
# Comparison Predicate Rules Sub-Package

## Purpose
Predicate rules comparing an input value against a fixed target or range
using Python's standard ordering and equality operators (`==`, `!=`, `<`,
`<=`, `>`, `>=`).

## Internal Components Registry

| Component           | Type  | Description                                                              |
| :---------------------| :---- | :---------------------------------------------------------------------------|
| `Equals`              | Class | Value must be equal (`==`) to an expected target.                       |
| `NotEquals`           | Class | Value must not be equal (`!=`) to a forbidden value.                    |
| `GreaterThan`         | Class | Value must be strictly greater than (`>`) a threshold.                  |
| `GreaterOrEqual`      | Class | Value must be greater than or equal to (`>=`) a threshold.              |
| `LessThan`            | Class | Value must be strictly less than (`<`) a threshold.                     |
| `LessOrEqual`         | Class | Value must be less than or equal to (`<=`) a threshold.                 |
| `InRange`             | Class | Value must fall within a `[min_val, max_val]` range (bounds configurable). |
"""
