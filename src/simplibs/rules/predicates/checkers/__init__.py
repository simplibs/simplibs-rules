from .IsEmpty import IsEmpty
from .IsFalse import IsFalse
from .IsNone import IsNone
from .IsTrue import IsTrue
from .NotEmpty import NotEmpty


_DESIGN_NOTES = """
# Checker Predicate Rules Sub-Package

## Purpose
Zero-parameter predicate rules that check a single, fixed property of the
input value — strict identity against `None`/`True`/`False`, or an empty vs.
non-empty length. None of these rules take constructor arguments.

## Internal Components Registry

| Component    | Type  | Description                                                              |
| :-------------| :---- | :---------------------------------------------------------------------------|
| `IsEmpty`     | Class | Value must be empty (`len(value) == 0`).                                |
| `NotEmpty`    | Class | Value must not be empty (`len(value) > 0`).                             |
| `IsNone`      | Class | Value must be the `None` singleton.                                     |
| `IsTrue`      | Class | Value must be the literal boolean `True` (strict identity).             |
| `IsFalse`     | Class | Value must be the literal boolean `False` (strict identity).            |
"""
