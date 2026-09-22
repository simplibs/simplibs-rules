from .raise_unsupported_annotation_error import raise_unsupported_annotation_error


_DESIGN_NOTES = """
# Typing Validations Sub-Package

## Purpose
Diagnostic exception helpers dedicated to type annotation decomposition failures
within `IsTyping`.

## Internal Components Registry

| Component                             | Type     | Description                                                                     |
| :------------------------------------ | :------- | :------------------------------------------------------------------------------ |
| `raise_unsupported_annotation_error`  | Function | Raises a structured ParamError for unrecognized or unsupported typing constructs.|
"""