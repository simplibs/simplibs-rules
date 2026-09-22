from .CloseTo import CloseTo
from .DivisibleBy import DivisibleBy
from .HasRemainder import HasRemainder


_DESIGN_NOTES = """
# Arithmetic Predicate Rules Sub-Package

## Purpose
Predicate rules validating numeric relationships between an input value and
a mathematically defined target — approximate equality, divisibility, and
modular remainder constraints.

## Internal Components Registry

| Component        | Type  | Description                                                              |
| :------------------| :---- | :---------------------------------------------------------------------------|
| `CloseTo`          | Class | Value must be close to a target within a relative/absolute tolerance.   |
| `DivisibleBy`      | Class | Value must be evenly divisible by a given divisor.                      |
| `HasRemainder`     | Class | Value must give a specific remainder when divided by a divisor.         |
"""
