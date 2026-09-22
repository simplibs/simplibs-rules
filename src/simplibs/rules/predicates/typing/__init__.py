from .IsAny import IsAny
from .IsTyping import IsTyping
from .build_typing_rule import build_typing_rule
from .tools.get_supported_origins import get_supported_origins
from .tools.is_supported_annotation import is_supported_annotation


_DESIGN_NOTES = """
# Typing Rules Sub-Package

## Purpose
Rules and structural builders for validating values against Python `typing`
annotations. Decomposes primitive types, generics, containers, unions, and
metadata into composed executable rule trees.

## Internal Components Registry

| Component                 | Type     | Description                                                                     |
| :------------------------ | :------- | :------------------------------------------------------------------------------ |
| `IsAny`                   | Rule     | Structural counterpart to `typing.Any` that accepts any value.                   |
| `IsTyping`                | Rule     | Main rule for validating values against arbitrary supported type annotations.  |
| `build_typing_rule`       | Function | Core entrypoint builder that translates type annotations into Rule instances.   |
| `get_supported_origins`   | Function | Utility returning set of supported origins handled by the builder registry.     |
| `is_supported_annotation` | Function | Utility checking whether a type annotation can be processed by `IsTyping`.     |

"""