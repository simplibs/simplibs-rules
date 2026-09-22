"""Public testing tools and assertion contracts for simplibs-rules."""

from .assert_rule_contract import assert_rule_contract
from .asserts import (
    assert_rule_build_exception,
    assert_rule_is_valid,
    assert_rule_param_error,
    assert_rule_raise_invalid,
    assert_rule_validate,
)

__all__ = [
    "assert_rule_contract",
    "assert_rule_build_exception",
    "assert_rule_is_valid",
    "assert_rule_param_error",
    "assert_rule_raise_invalid",
    "assert_rule_validate",
]


_DESIGN_NOTES = """
# Testing Utilities Sub-Package

## Purpose
Public testing package exporting assertion helpers, wrapper validation suite
checkers, and the master contract orchestrator used to verify validation rule
implementations across the library ecosystem.

## Exported Components Registry

| Component                      | Type     | Description                                                                 |
| :----------------------------- | :------- | :-------------------------------------------------------------------------- |
| `assert_rule_contract`         | Function | Master contract test orchestrator validating end-to-end rule behavior.       |
| `assert_rule_build_exception`  | Function | Verifies that `build_exception()` yields expected `ValidationError` cards.  |
| `assert_rule_is_valid`         | Function | Asserts boolean `is_valid()` results across valid and invalid inputs.        |
| `assert_rule_param_error`      | Function | Verifies that rule instantiation fails properly on invalid init arguments.  |
| `assert_rule_raise_invalid`    | Function | Verifies that `raise_invalid()` raises the expected `ValidationError`.      |
| `assert_rule_validate`         | Function | Verifies `validate()` execution, pass-through return values, and errors.    |
"""