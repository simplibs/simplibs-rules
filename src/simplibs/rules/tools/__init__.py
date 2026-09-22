from .raise_invalid import raise_invalid


_DESIGN_NOTES = """
# Tools Sub-Package

## Purpose
Provides standalone operational helper utilities that operate alongside the Rule engine,
enabling direct exception triggers and control flow shortcuts without re-evaluating conditions.

## Registry

| Component       | Type     | Description                                                                     |
| :-------------- | :------- | :------------------------------------------------------------------------------ |
| `raise_invalid` | Function | Unconditionally constructs and raises a ValidationError for a given rule/callable. |
"""