import pytest
from simplibs.rules.containers._helpers.format_key_label import format_key_label


@pytest.mark.parametrize(
    "key, value_name, expected",
    [
        ("zz", "opts", "opts[key 'zz']"),
        (1, "opts", "opts[key 1]"),
        (("x", 1), "opts", "opts[key ('x', 1)]"),
        (None, "opts", "opts[key None]"),
        (2.5, "opts", "opts[key 2.5]"),
        ("zz", "config['db']", "config['db'][key 'zz']"),
    ],
    ids=["str key", "int key", "tuple key", "None key", "float key", "nested name"],
)
def test_format_key_label_marks_the_key_as_a_key(key, value_name, expected) -> None:
    """Verify the label is the name followed by a bracket with the word 'key' and the repr of the key."""
    assert format_key_label(key, value_name) == expected


@pytest.mark.parametrize(
    "key, expected",
    [
        ("zz", "[key 'zz']"),
        (1, "[key 1]"),
        (("x", 1), "[key ('x', 1)]"),
    ],
)
def test_format_key_label_without_a_name_keeps_only_the_bracket(key, expected) -> None:
    """Verify the bracket part stands alone when there is no name."""
    assert format_key_label(key) == expected
    assert format_key_label(key, None) == expected


def test_format_key_label_treats_an_empty_name_as_no_name() -> None:
    """Verify an empty string is handled like a missing name."""
    assert format_key_label("zz", "") == "[key 'zz']"


def test_format_key_label_shortens_a_long_key() -> None:
    """Verify the key part is cut to the fixed length, so the label stays readable."""
    key = "k" * 100

    label = format_key_label(key, "opts")

    assert label == f"opts[key {repr(key)[:37]}...]"
    assert len(label) == len("opts[key ") + 40 + len("]")


def test_format_key_label_differs_from_the_value_label_of_the_same_key() -> None:
    """Verify one key never gets the same label as a key and as a value."""
    from simplibs.rules.containers._helpers.format_value_label import format_value_label

    assert format_key_label("a", "opts") != format_value_label("a", "opts")
