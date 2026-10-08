import pytest
from simplibs.rules.base_class import Rule
from simplibs.rules.containers._helpers.describe_rule import describe_rule


# ----------------------------------------------------------------------
# Dummy Rules for Testing
# ----------------------------------------------------------------------

class _DummyBaseRule(Rule):
    """Shared plumbing: always valid, keeps the default describe()."""

    __slots__ = ()

    def is_valid(self, value: object) -> bool:
        return True

    def build_exception(
        self,
        value: object,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        return ValueError("Error")


class CustomNamedRule(_DummyBaseRule):
    """Rule that keeps the default description (its class name)."""

    __slots__ = ()


class DescribedRule(_DummyBaseRule):
    """Rule with its own description."""

    __slots__ = ()

    def describe(self) -> str:
        return "> 0"


class GroupRule(_DummyBaseRule):
    """Rule standing in for a compound container (the type listed in `parenthesize`)."""

    __slots__ = ()

    def describe(self) -> str:
        return "a | b"


class SubGroupRule(GroupRule):
    """Subclass of the parenthesized type."""

    __slots__ = ()


class RaisingDescribeRule(_DummyBaseRule):
    """Faulty rule: describe() raises."""

    __slots__ = ()

    def describe(self) -> str:
        raise RuntimeError("describe exploded")


class EmptyDescribeRule(_DummyBaseRule):
    """Faulty rule: describe() returns an empty string."""

    __slots__ = ()

    def describe(self) -> str:
        return ""


class NonStringDescribeRule(_DummyBaseRule):
    """Faulty rule: describe() returns a non-str value."""

    __slots__ = ()

    def describe(self) -> str:
        return 42  # type: ignore[return-value]


class CallableWithoutName:
    """Callable object without a __name__ attribute."""

    def __call__(self, value: object) -> bool:
        return True

    def __repr__(self) -> str:
        return "<CallableWithoutNameRepr>"


# ----------------------------------------------------------------------
# Rule instances
# ----------------------------------------------------------------------

def test_describe_rule_default_description_is_class_name() -> None:
    """Verify describe_rule yields the class name for a rule that keeps the default describe()."""
    assert describe_rule(CustomNamedRule()) == "CustomNamedRule"


def test_describe_rule_uses_rule_own_description() -> None:
    """Verify describe_rule delegates to Rule.describe() instead of using the class name."""
    assert describe_rule(DescribedRule()) == "> 0"


# ----------------------------------------------------------------------
# Plain callables
# ----------------------------------------------------------------------

def test_describe_rule_with_named_function() -> None:
    """Verify describe_rule extracts __name__ for standard functions."""

    def my_validation_function(val: object) -> bool:
        return True

    assert describe_rule(my_validation_function) == "my_validation_function"


def test_describe_rule_with_lambda() -> None:
    """Verify describe_rule extracts <lambda> for anonymous functions."""
    anon = lambda x: True
    assert describe_rule(anon) == "<lambda>"


def test_describe_rule_with_unnamed_callable_fallback() -> None:
    """Verify describe_rule falls back to repr(rule) when __name__ is absent."""
    obj = CallableWithoutName()
    assert describe_rule(obj) == "<CallableWithoutNameRepr>"


# ----------------------------------------------------------------------
# parenthesize
# ----------------------------------------------------------------------

def test_describe_rule_parenthesize(subtests) -> None:
    """Verify that only instances of the listed types are wrapped in parentheses."""

    with subtests.test("listed type is wrapped"):
        assert describe_rule(GroupRule(), parenthesize=(GroupRule,)) == "(a | b)"

    with subtests.test("subclass of a listed type is wrapped"):
        assert describe_rule(SubGroupRule(), parenthesize=(GroupRule,)) == "(a | b)"

    with subtests.test("unlisted type is not wrapped"):
        assert describe_rule(DescribedRule(), parenthesize=(GroupRule,)) == "> 0"

    with subtests.test("empty tuple wraps nothing"):
        assert describe_rule(GroupRule(), parenthesize=()) == "a | b"

    with subtests.test("default wraps nothing"):
        assert describe_rule(GroupRule()) == "a | b"

    with subtests.test("plain callable is never wrapped"):
        def is_positive(value: object) -> bool:
            return True

        assert describe_rule(is_positive, parenthesize=(GroupRule,)) == "is_positive"


# ----------------------------------------------------------------------
# Defensive boundary: a faulty describe() must not mask the real error
# ----------------------------------------------------------------------

def test_describe_rule_faulty_describe_falls_back_to_class_name(subtests) -> None:
    """Verify that a raising, empty or non-str describe() is replaced by the class name."""

    with subtests.test("describe raises"):
        assert describe_rule(RaisingDescribeRule()) == "RaisingDescribeRule"

    with subtests.test("describe returns empty string"):
        assert describe_rule(EmptyDescribeRule()) == "EmptyDescribeRule"

    with subtests.test("describe returns non-str"):
        assert describe_rule(NonStringDescribeRule()) == "NonStringDescribeRule"


def test_describe_rule_faulty_describe_fallback_is_still_parenthesized() -> None:
    """Verify that the class-name fallback is wrapped too when the rule's type is listed."""
    assert (
        describe_rule(RaisingDescribeRule(), parenthesize=(RaisingDescribeRule,))
        == "(RaisingDescribeRule)"
    )
