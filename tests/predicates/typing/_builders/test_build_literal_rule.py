from typing import Literal

from simplibs.rules.predicates.logic import IsIn
from simplibs.rules.predicates.typing._builders.build_literal_rule import (
    build_literal_rule,
)


def test_build_literal_rule_values() -> None:
    """Verify Literal values turn into an IsIn rule with strict=True."""
    rule = build_literal_rule(Literal["read", "write", 1])

    assert isinstance(rule, IsIn)
    assert rule.strict is True

    # Ověření přes veřejné chování (povoleno / zamítnuto)
    assert rule.is_valid("read") is True
    assert rule.is_valid("write") is True
    assert rule.is_valid(1) is True
    assert rule.is_valid("execute") is False


def test_build_literal_rule_strict_type_checking() -> None:
    """Verify Literal[1] rejects True due to strict type matching (1 != True in strict mode)."""
    rule = build_literal_rule(Literal[1])

    assert isinstance(rule, IsIn)
    assert rule.is_valid(1) is True
    assert rule.is_valid(True) is False  # V Pythonu 1 == True, ale strict=True to musí zamítnout!