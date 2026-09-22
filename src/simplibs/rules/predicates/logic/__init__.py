from .Is import Is
from .IsIn import IsIn
from .IsNot import IsNot
from .NotIn import NotIn
from .UserRule import UserRule

_DESIGN_NOTES = """
# Logic Predicate Rules Sub-Package

## Purpose
Predicate rules built on Python's identity (`is`), membership (`in`), and arbitrary
custom callable predicates — checking exact object identity, presence/absence within
a reference collection, or user-defined boolean conditions.

## Internal Components Registry

| Component   | Type  | Description                                                              |
| :---------- | :---- | :----------------------------------------------------------------------- |
| `Is`        | Class | Value must be identical (`is`) to a specific object.                     |
| `IsIn`      | Class | Value must be a member of a given collection.                            |
| `IsNot`     | Class | Value must NOT be identical (`is not`) to a specific object.             |
| `NotIn`     | Class | Value must NOT be a member of a given collection.                        |
| `UserRule`  | Class | Value must satisfy an arbitrary user-supplied callable predicate.        |
"""