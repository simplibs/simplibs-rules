from .format_annotation import format_annotation


_DESIGN_NOTES = """
# Typing Helpers Sub-Package

## Purpose
Shared helpers used internally by the typing package. They are not part of
the public surface (the folder starts with an underscore, so nothing here is
re-exported by `predicates/typing/__init__.py`).

## Internal Components Registry

| Component           | Type     | Description                                                                          |
| :------------------ | :------- | :----------------------------------------------------------------------------------- |
| `format_annotation` | Function | Returns a compact, readable spelling of an annotation ("list[int]", "int | None"). |
"""
