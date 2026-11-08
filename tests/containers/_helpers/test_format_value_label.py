import pytest
from simplibs.rules.containers._helpers.format_value_label import format_value_label


@pytest.mark.parametrize(
    "key, value_name, expected",
    [
        ("b", "opts", "opts['b']"),
        (2, "opts", "opts[2]"),
        (("x", 1), "opts", "opts[('x', 1)]"),
        (None, "opts", "opts[None]"),
        (2.5, "opts", "opts[2.5]"),
        ("b", "config['db']", "config['db']['b']"),
    ],
    ids=["str key", "int key", "tuple key", "None key", "float key", "nested name"],
)
def test_format_value_label_spells_the_access_in_python(key, value_name, expected) -> None:
    """Verify the label reads like indexing the mapping: name followed by the repr of the key."""
    assert format_value_label(key, value_name) == expected


@pytest.mark.parametrize(
    "key, expected",
    [
        ("b", "['b']"),
        (2, "[2]"),
        (("x", 1), "[('x', 1)]"),
    ],
)
def test_format_value_label_without_a_name_keeps_only_the_bracket(key, expected) -> None:
    """Verify the bracket part stands alone when there is no name."""
    assert format_value_label(key) == expected
    assert format_value_label(key, None) == expected


def test_format_value_label_treats_an_empty_name_as_no_name() -> None:
    """Verify an empty string does not produce a label that starts with a bare bracket after nothing."""
    assert format_value_label("b", "") == "['b']"


def test_format_value_label_shortens_a_long_key() -> None:
    """Verify the key part is cut to the fixed length, so the label stays readable."""
    key = "k" * 100

    label = format_value_label(key, "opts")

    assert label == f"opts[{repr(key)[:37]}...]"
    assert len(label) == len("opts[") + 40 + len("]")


def test_format_value_label_is_never_marked_as_a_key() -> None:
    """Verify a value label carries no 'key' marker, that is what separates it from a key label."""
    assert "key" not in format_value_label(1, "opts")
