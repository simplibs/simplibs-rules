"""Granular assertion helpers for testing individual validation rule methods."""

from .assert_rule_build_exception import assert_rule_build_exception
from .assert_rule_is_valid import assert_rule_is_valid
from .assert_rule_param_error import assert_rule_param_error
from .assert_rule_validate import assert_rule_validate


_DESIGN_NOTES = """
# Rule Asserts Sub-Package

## Purpose
Internal assertions module providing granular test helpers for individual methods
of validation rules (`is_valid`, `validate`, `build_exception`, and constructor `ParamError` validation).

## Exported Components Registry

| Component                      | Type     | Description                                                                 |
| :----------------------------- | :------- | :-------------------------------------------------------------------------- |
| `assert_rule_build_exception`  | Function | Verifies that `build_exception()` yields expected `ValidationError` cards.  |
| `assert_rule_is_valid`         | Function | Asserts boolean `is_valid()` results across valid and invalid inputs.        |
| `assert_rule_param_error`      | Function | Verifies that rule instantiation fails properly on invalid init arguments.  |
| `assert_rule_validate`         | Function | Verifies `validate()` execution, pass-through return values, and errors.    |
"""