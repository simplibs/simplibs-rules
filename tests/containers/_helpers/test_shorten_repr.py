import pytest
from simplibs.rules.containers._helpers.shorten_repr import shorten_repr


@pytest.mark.parametrize(
    "value, expected",
    [
        ("abc", "'abc'"),
        (12345, "12345"),
        (None, "None"),
        ((1, "x"), "(1, 'x')"),
        (2.5, "2.5"),
        ("", "''"),
    ],
)
def test_shorten_repr_returns_a_short_repr_as_it_is(value, expected) -> None:
    """Verify a repr within the limit passes through untouched."""
    assert shorten_repr(value) == expected


def test_shorten_repr_keeps_a_repr_of_exactly_the_limit() -> None:
    """Verify the limit itself is allowed: 38 characters plus two quotes is 40."""
    value = "a" * 38

    assert len(repr(value)) == 40
    assert shorten_repr(value) == repr(value)


def test_shorten_repr_cuts_a_repr_one_character_over_the_limit() -> None:
    """Verify 41 characters become 37 of the repr and three dots."""
    value = "a" * 39

    result = shorten_repr(value)

    assert len(repr(value)) == 41
    assert result == repr(value)[:37] + "..."
    assert len(result) == 40


def test_shorten_repr_cuts_a_very_long_value() -> None:
    """Verify a long key is reduced to the limit, quote at the start and no closing quote."""
    result = shorten_repr("k" * 500)

    assert result.startswith("'kkk")
    assert result.endswith("...")
    assert len(result) == 40


def test_shorten_repr_respects_a_custom_limit() -> None:
    """Verify max_length is the length of the result, dots included."""
    assert shorten_repr("abcdefghij", 8) == "'abcd..."
    assert shorten_repr("abcdefghij", 12) == "'abcdefghij'"


def test_shorten_repr_with_limit_equal_to_the_dots() -> None:
    """Verify a limit of three leaves nothing but the dots."""
    assert shorten_repr("abcdef", 3) == "..."


def test_shorten_repr_never_exceeds_the_limit(subtests) -> None:
    """Verify the result is never longer than max_length for any limit of at least 3."""
    value = "x" * 100

    for limit in range(3, 60):
        with subtests.test(f"max_length={limit}"):
            assert len(shorten_repr(value, limit)) <= limit


def test_shorten_repr_works_on_composite_values() -> None:
    """Verify tuples and frozensets are shortened by their repr like anything else."""
    value = tuple(range(100))

    result = shorten_repr(value)

    assert result.startswith("(0, 1, 2")
    assert result.endswith("...")
    assert len(result) == 40
