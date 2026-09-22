from .AllUnique import AllUnique
from .HasItem import HasItem
from .HasKey import HasKey
from .HasKeys import HasKeys
from .IsContainer import IsContainer
from .IsSubsetOf import IsSubsetOf
from .IsSupersetOf import IsSupersetOf


_DESIGN_NOTES = """
# Collection Predicate Rules Sub-Package

## Purpose
Predicate rules operating on containers, mappings, and iterables —
uniqueness, item/key membership, container type identity, and
set-relationship checks (subset/superset) against a reference collection.

## Internal Components Registry

| Component        | Type  | Description                                                              |
| :------------------| :---- | :---------------------------------------------------------------------------|
| `AllUnique`        | Class | Every item in an iterable must be unique (no duplicates).               |
| `HasItem`          | Class | Container value must contain a single given item.                       |
| `HasKey`           | Class | Mapping value must contain a single given key.                          |
| `HasKeys`          | Class | Mapping value must contain all of the given keys.                       |
| `IsContainer`      | Class | Value must be a non-string collection/container.                        |
| `IsSubsetOf`       | Class | Value (as a set) must be a subset of a reference collection.            |
| `IsSupersetOf`     | Class | Value (as a set) must be a superset of a reference collection.          |
"""