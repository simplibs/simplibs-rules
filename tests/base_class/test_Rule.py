"""Tests for the base Rule abstraction, typing integration, and operator composition."""

from typing import Annotated, get_args, get_origin
import pytest
from simplibs.rules.base_class import Rule
from simplibs.rules.containers.AllOf import AllOf
from simplibs.rules.containers.AnyOf import AnyOf
from simplibs.rules.containers.Not import Not


class DummyPassRule(Rule):
    """Dummy rule that always passes."""

    def is_valid(self, value: object) -> bool:
        return True

    def build_exception(
        self,
        value: object,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        return ValueError("Dummy pass failure")


class DummyFailRule(Rule):
    """Dummy rule that always fails."""

    def is_valid(self, value: object) -> bool:
        return False

    def build_exception(
        self,
        value: object,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        label = value_name or "value"
        ctx = f" [{context}]" if context else ""
        return ValueError(f"Validation failed for {label}{ctx} with {value!r}")


# ==============================================================================
# 1. BASE RULE INTERFACE TESTS
# ==============================================================================

def test_rule_abstract_instantiation() -> None:
    """Verify that Rule cannot be instantiated directly."""
    with pytest.raises(TypeError):
        Rule()  # type: ignore[abstract]


def test_rule_call_magic_method() -> None:
    """Verify that calling the rule instance delegates directly to is_valid."""
    pass_rule = DummyPassRule()
    fail_rule = DummyFailRule()

    assert pass_rule("anything") is True
    assert fail_rule("anything") is False


def test_rule_validate_success_default() -> None:
    """Verify validate returns True on success by default."""
    rule = DummyPassRule()
    assert rule.validate("test_val") is True


def test_rule_validate_success_return_value() -> None:
    """Verify validate returns the original value when return_value=True."""
    rule = DummyPassRule()
    val = {"key": "value"}
    assert rule.validate(val, return_value=True) is val


def test_rule_validate_failure_raises_exception() -> None:
    """Verify validate raises built exception on failure by default."""
    rule = DummyFailRule()
    with pytest.raises(ValueError, match="Validation failed for custom_name \\[test_ctx\\] with 'bad_val'"):
        rule.validate("bad_val", value_name="custom_name", context="test_ctx")


def test_rule_validate_failure_return_bool() -> None:
    """Verify validate returns False on failure when return_bool=True."""
    rule = DummyFailRule()
    assert rule.validate("bad_val", return_bool=True) is False


# ==============================================================================
# 2. TYPING INTEGRATION TESTS (.annotated())
# ==============================================================================

def test_rule_annotated_method(subtests) -> None:
    """Verify functionality of the .annotated() method for typing integration."""
    rule = DummyPassRule()

    with subtests.test("returns correct Annotated structure"):
        annotated_type = rule.annotated(int)
        assert get_origin(annotated_type) is Annotated

        args = get_args(annotated_type)
        assert args[0] is int
        assert args[1] is rule

    with subtests.test("works with complex composition"):
        pass_rule = DummyPassRule()
        fail_rule = DummyFailRule()
        composed_rule = pass_rule & ~fail_rule

        annotated_str = composed_rule.annotated(str)
        assert get_origin(annotated_str) is Annotated

        args = get_args(annotated_str)
        assert args[0] is str
        assert args[1] is composed_rule


# ==============================================================================
# 3. OPERATOR COMPOSITION TESTS (|, &, ~)
# ==============================================================================

def test_rule_operator_or(subtests) -> None:
    """Verify functionality of the | operator (OR / AnyOf)."""
    pass_rule = DummyPassRule()
    fail_rule = DummyFailRule()
    fn_true = lambda x: True

    with subtests.test("rule | rule"):
        combined = fail_rule | pass_rule
        assert isinstance(combined, AnyOf)
        assert combined.is_valid("test") is True

    with subtests.test("rule | callable"):
        combined = fail_rule | fn_true
        assert isinstance(combined, AnyOf)
        assert combined.is_valid("test") is True

    with subtests.test("callable | rule (via __ror__)"):
        combined = fn_true | fail_rule
        assert isinstance(combined, AnyOf)
        assert combined.is_valid("test") is True


def test_rule_operator_and(subtests) -> None:
    """Verify functionality of the & operator (AND / AllOf)."""
    pass_rule = DummyPassRule()
    fail_rule = DummyFailRule()
    fn_true = lambda x: True

    with subtests.test("rule & rule"):
        combined = pass_rule & fail_rule
        assert isinstance(combined, AllOf)
        assert combined.is_valid("test") is False

    with subtests.test("rule & callable"):
        combined = pass_rule & fn_true
        assert isinstance(combined, AllOf)
        assert combined.is_valid("test") is True

    with subtests.test("callable & rule (via __rand__)"):
        combined = fn_true & pass_rule
        assert isinstance(combined, AllOf)
        assert combined.is_valid("test") is True


def test_rule_operator_invert() -> None:
    """Verify functionality of the ~ operator (NOT / Not)."""
    pass_rule = DummyPassRule()
    inverted = ~pass_rule

    assert isinstance(inverted, Not)
    assert inverted.is_valid("test") is False


def test_rule_operators_invalid_type(subtests) -> None:
    """Verify that operators with invalid types raise TypeError (via NotImplemented)."""
    rule = DummyPassRule()
    invalid_operand = 12345

    with subtests.test("rule | invalid"):
        with pytest.raises(TypeError):
            _ = rule | invalid_operand  # type: ignore[operator]

    with subtests.test("invalid | rule"):
        with pytest.raises(TypeError):
            _ = invalid_operand | rule  # type: ignore[operator]

    with subtests.test("rule & invalid"):
        with pytest.raises(TypeError):
            _ = rule & invalid_operand  # type: ignore[operator]

    with subtests.test("invalid & rule"):
        with pytest.raises(TypeError):
            _ = invalid_operand & rule  # type: ignore[operator]


def test_rule_complex_operator_composition() -> None:
    """Verify complex expressions with multiple operators."""
    p1 = DummyPassRule()
    p2 = DummyPassRule()
    f1 = DummyFailRule()

    # Expression: (Pass AND Fail) OR (NOT Fail) -> False OR True -> True
    complex_rule = (p1 & f1) | (~f1)
    assert isinstance(complex_rule, AnyOf)
    assert complex_rule.is_valid("test") is True