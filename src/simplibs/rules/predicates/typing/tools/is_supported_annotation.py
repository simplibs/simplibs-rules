from typing import Any
# Outers
from simplibs.exception import ParamError
from ..build_typing_rule import build_typing_rule


def is_supported_annotation(annotation: Any) -> bool:
    """Check whether a given type annotation is supported by the validation engine.

    This recursively inspects the annotation (including nested generic arguments)
    by attempting to compile it via `build_typing_rule`.

    Args:
        annotation: Any type annotation, class, or typing construct to inspect.

    Returns:
        True if the annotation can be successfully compiled into a Rule,
        False if it contains unsupported constructs (e.g. bare TypeVar,
        unparsed ForwardRef, or unknown objects).
    """
    try:
        build_typing_rule(annotation)
        return True
    except ParamError:
        return False


_DESIGN_NOTES = """
# is_supported_annotation — Type Annotation Safeguard Predicate

## Purpose
A lightweight, boolean predicate utility designed to verify whether a given type
annotation, class, or typing expression can be successfully compiled into a
Rule by the validation system.

---

## 1. Non-Raising Inspection Logic

Delegates execution directly to `build_typing_rule(annotation)` wrapped in a
`try-except` block. Instead of raising exceptions on unsupported objects, bare
`TypeVar` definitions, or unparsed `ForwardRef` instances, it catches internal
`ParamError` exceptions and gracefully returns `False`.

---

## 2. Deep Structural Decomposition

Because `build_typing_rule` recursively traverses all inner generic arguments
(e.g., nested `Union`, `tuple`, or `dict` shapes), `is_supported_annotation`
validates the entire annotation hierarchy down to its leaf nodes.

---

## 3. Runtime Probe Safeguard

Acts as an architectural safeguard for higher-level decorators and dynamic
validators, allowing them to inspect annotation compatibility prior to full
compilation or function invocation.
"""