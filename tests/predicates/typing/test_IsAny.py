"""Tests for the IsAny rule."""

import pytest

# Testing tools
from simplibs.rules.testing import assert_rule_contract

# Exceptions
from simplibs.exception import ValidationError

# Rules
from simplibs.rules.predicates.typing.IsAny import IsAny


# ==============================================================================
# 1. MASTER CONTRACT TEST
# ==============================================================================

def test_is_any_contract(subtests):
    """Verify the complete contract of IsAny using the master orchestrator."""
    rule = IsAny()

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, "string", [1, 2], {"a": 1}, None, True, object()],
        invalid_values=[],  # IsAny acceptuje absolutně cokoliv
        rule_factory=IsAny,
        deep_check=True,
        verbose=False,
    )


# ==============================================================================
# 2. DIRECT EXCEPTION CARD TEST (Unreachable fallback method check)
# ==============================================================================

def test_is_any_build_exception_fallback():
    """Verify build_exception directly for coverage even though is_valid never fails."""
    rule = IsAny()

    # Zavoláme metodu přímo a ověříme zkonstruovaný objekt výjimky
    exc = rule.build_exception("test_val", value_name="sample")

    assert isinstance(exc, ValidationError)
    assert exc.label == "sample"
    assert exc.expected == "any value"
    assert exc.problem == "IsAny.is_valid() unexpectedly returned False."