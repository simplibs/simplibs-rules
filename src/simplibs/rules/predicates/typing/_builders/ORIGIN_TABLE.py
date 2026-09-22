from collections import abc as collections_abc
import types
import typing
# Inners
from .build_annotated_rule import build_annotated_rule
from .build_any_of_rule import build_any_of_rule
from .build_callable_rule import build_callable_rule
from .build_elements_rule import build_elements_rule
from .build_key_value_rule import build_key_value_rule
from .build_literal_rule import build_literal_rule
from .build_tuple_rule import build_tuple_rule
from .build_type_rule import build_type_rule


ORIGIN_TABLE = {

    # ---- ELEMENTS — container + rule per item -----------------------------
    list: build_elements_rule,
    set: build_elements_rule,
    frozenset: build_elements_rule,
    # collections.abc
    collections_abc.Iterable: build_elements_rule,
    collections_abc.Sequence: build_elements_rule,
    collections_abc.Collection: build_elements_rule,
    # typing
    typing.Iterable: build_elements_rule,
    typing.Sequence: build_elements_rule,
    typing.Collection: build_elements_rule,

    # ---- TUPLE — tuple[T, ...] / tuple[A, B, C] ----------------------------
    tuple: build_tuple_rule,

    # ---- KEY_VALUE — mapping + rule(key) + rule(value) ---------------------
    dict: build_key_value_rule,
    # collections.abc
    collections_abc.Mapping: build_key_value_rule,
    collections_abc.MutableMapping: build_key_value_rule,
    # typing
    typing.Mapping: build_key_value_rule,
    typing.MutableMapping: build_key_value_rule,

    # ---- ANY_OF — Union[...] / X | Y ---------------------------------------
    typing.Union: build_any_of_rule,
    types.UnionType: build_any_of_rule,

    # ---- LITERAL — Literal[...] ---------------------------------------------
    typing.Literal: build_literal_rule,

    # ---- TYPE — Type[T] / type[T] --------------------------------------------
    type: build_type_rule,
    typing.Type: build_type_rule,

    # ---- CALLABLE — Callable[[...], R] ---------------------------------------
    collections_abc.Callable: build_callable_rule,
    typing.Callable: build_callable_rule,

    # ---- ANNOTATED — Annotated[T, ...metadata...] ---------------------------
    typing.Annotated: build_annotated_rule,

    # Legacy typing aliases for built-in containers (for backward compatibility)
    typing.List: build_elements_rule,
    typing.Set: build_elements_rule,
    typing.FrozenSet: build_elements_rule,
    typing.Tuple: build_tuple_rule,
    typing.Dict: build_key_value_rule,
}


_DESIGN_NOTES = """
# _origin_table — Origin → Process Lookup

## Purpose
A static registry mapping supported `get_origin()` results to their respective
builder functions. This mapping translates typing constructs into specific Rule
builder processes. It is defined as a simple dictionary since all origin keys and
their corresponding builders are static and fully known at import time.

---

## 1. Multiple Origins Map to Shared Builder Logic

Multiple origin keys share the same builder where structural validation semantics
overlap. For instance, `list`, `set`, `frozenset`, and generic collection ABCs
(`Iterable`, `Sequence`, `Collection`) all map to `build_elements_rule`. This allows
numerous typing constructs to collapse onto a compact set of standardized builders.

---

## 2. Unconditional Module-Load Imports

All builders are imported at module load time directly from the `.builders`
sub-package. Because the origin table is constructed once during initialization,
every builder function must be available upfront.

---

## 3. Tuple Origin Handling via `build_tuple_rule`

The `tuple` origin maps to `build_tuple_rule`, which evaluates `get_args()`
to determine whether to apply the ELEMENTS process (for unbounded homogeneous
`tuple[T, ...]`) or the POSITIONAL process (for fixed-length heterogeneous
`tuple[A, B, C]`).

---

## 4. Native `Annotated` Dispatch

Targeting Python 3.11+ guarantees that `get_origin(Annotated[...])` consistently
returns `typing.Annotated`. Consequently, `Annotated` is registered directly in this
table alongside other origin types, invoking `build_annotated_rule` to process
embedded metadata rules.
"""