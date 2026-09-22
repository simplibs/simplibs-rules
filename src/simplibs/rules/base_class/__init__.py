from .Rule import Rule


_DESIGN_NOTES = """
# Rule Base Class Sub-Package

## Purpose
Holds the abstract base class that every concrete validation rule in the
library inherits from, defining the common evaluation and exception-building
contract.

## Internal Components Registry

| Component | Type  | Description                                                                     |
| :-------- | :---- | :------------------------------------------------------------------------------|
| `Rule`    | Class | Abstract base class defining `is_valid`, `build_exception`, `__call__`, `validate`. |
"""