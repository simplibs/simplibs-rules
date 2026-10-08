from typing import Any
from simplibs.exception.testing import maybe_subtest
# Outers
from ...base_class import Rule


def assert_rule_slots(
    subtests: Any,
    rule: Rule,
    *,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that a rule instance carries no per-instance `__dict__`.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        rule: The Rule instance under test.
        verbose: Enables isolated pytest subtest tracking for the check.
        intro: Optional prefix string added to generated subtest identity names.
    """
    assert isinstance(rule, Rule), (
        f"assert_rule_slots expects a Rule instance, got {type(rule).__name__}."
    )

    with maybe_subtest(
        subtests,
        name=f"{intro}test_no_instance_dict",
        verbose=verbose,
    ):
        offenders = [
            cls.__name__
            for cls in type(rule).__mro__
            if cls is not object and "__slots__" not in vars(cls)
        ]
        assert not hasattr(rule, "__dict__"), (
            f"{type(rule).__name__} instances carry a __dict__, so __slots__ saves "
            f"nothing. Every class in the hierarchy must declare __slots__ "
            f"(an empty tuple if it adds no attributes). "
            f"Classes without __slots__: {offenders}."
        )


_DESIGN_NOTES = """
# assert_rule_slots (Slots Integrity Blade)

## Purpose
Guards the `__slots__` convention: `Rule` declares `__slots__ = ()` and every
subclass declares its own attributes. A single class in the hierarchy that
forgets `__slots__` silently gives every instance a `__dict__` again, and
the slots declared elsewhere stop saving memory or blocking stray attributes.

---

## 1. Why `hasattr(rule, "__dict__")`

It is the exact property that matters: on a fully slotted instance the
attribute does not exist. Checking each class for `__slots__` alone would
miss a base class outside this library.

---

## 2. Offender List

The failure message names every class in the MRO that has no `__slots__`
of its own, so the missing declaration is found without a debugger.
"""
