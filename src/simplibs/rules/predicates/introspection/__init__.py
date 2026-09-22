from .HasAttribute import HasAttribute
from .HasLength import HasLength
from .IsCallable import IsCallable
from .IsDataclass import IsDataclass
from .IsHashable import IsHashable
from .IsInstance import IsInstance
from .IsIterable import IsIterable
from .IsSubclass import IsSubclass
from .IsType import IsType


_DESIGN_NOTES = """
# Introspection Predicate Rules Sub-Package

## Purpose
Predicate rules that inspect the structural or behavioral properties of a
value — its type, class hierarchy, length, or the protocols it implements
(callable, hashable, iterable, attribute presence) — rather than its
concrete contents.

## Internal Components Registry

| Component         | Type  | Description                                                              |
| :--------------------| :---- | :---------------------------------------------------------------------------|
| `HasAttribute`       | Class | Value must have a given attribute or method (duck typing).              |
| `HasLength`          | Class | Value's `len()` must equal a target, or fall within min/max bounds.     |
| `IsCallable`         | Class | Value must be callable.                                                 |
| `IsDataclass`        | Class | Value must be a dataclass instance or class.                            |
| `IsHashable`         | Class | Value must be hashable.                                                 |
| `IsInstance`         | Class | Value must be an instance of one or more given types.                   |
| `IsIterable`         | Class | Value must be iterable.                                                 |
| `IsSubclass`         | Class | Value must be a class that is a subclass of one or more given types.    |
| `IsType`             | Class | Value must itself be a class/type object, not an instance.              |
"""
