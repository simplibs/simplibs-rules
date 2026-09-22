from .get_supported_origins import get_supported_origins
from .is_supported_annotation import is_supported_annotation


_DESIGN_NOTES = """
# Typing Tools Sub-Package

## Purpose
Utility functions for checking and inspecting Python typing annotations,
allowing safe pre-validation and discovery of supported origins before
rule decomposition.

## Internal Components Registry

| Component                 | Type     | Description                                                                     |
| :------------------------ | :------- | :------------------------------------------------------------------------------ |
| `get_supported_origins`   | Function | Returns a set of supported typing origin types handled by the typing subsystem. |
| `is_supported_annotation` | Function | Checks whether a given type annotation is supported for rule construction.      |

"""