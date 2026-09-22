from .IsBool import IsBool
from .IsInteger import IsInteger
from .IsFloat import IsFloat
from .IsDecimal import IsDecimal
from .IsNumber import IsNumber
from .IsPrimitiveNumber import IsPrimitiveNumber
from .IsZero import IsZero
from .IsNan import IsNan
from .IsInfinity import IsInfinity
from .IsPi import IsPi
from .IsEven import IsEven
from .IsOdd import IsOdd
from .IsFinite import IsFinite


_DESIGN_NOTES = """
# Numeric Predicate Rules Sub-Package

## Purpose
Predicate rules validating numeric type identity and special numeric
values — exact type membership (`int`, `float`, `Decimal`), the general
vs. primitive numeric umbrella, zero, NaN, infinity, and the mathematical
constant Pi.

## Internal Components Registry

| Component            | Type  | Description                                                              |
| :------------------- | :---- | :----------------------------------------------------------------------- |
| `IsBool`             | Class | Value must be a `bool`.                                                  |
| `IsInteger`          | Class | Value must be an `int` (booleans excluded).                              |
| `IsFloat`            | Class | Value must be strictly a `float`.                                        |
| `IsDecimal`          | Class | Value must be a `decimal.Decimal`.                                       |
| `IsNumber`           | Class | Value must be any numeric type (`int`, `float`, `Decimal`, `complex`).   |
| `IsPrimitiveNumber`  | Class | Value must be `int` or `float` (booleans excluded).                      |
| `IsZero`             | Class | Numeric value must equal zero.                                           |
| `IsNan`              | Class | Value must be a float NaN.                                               |
| `IsInfinity`         | Class | Value must be positive or negative infinity.                             |
| `IsPi`               | Class | Value must equal `math.pi` when rounded to N decimal places.             |
| `IsEven`             | Class | Value must be an even integer (booleans excluded).                       |
| `IsOdd`              | Class | Value must be an odd integer (booleans excluded).                        |
| `IsFinite`           | Class | Value must be a primitive number (int/float) that is neither NaN nor inf.|
"""
