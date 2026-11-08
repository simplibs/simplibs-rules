from typing import Any


def shorten_repr(value: Any, max_length: int = 40) -> str:
    """Return `repr(value)`, cut to `max_length` characters with three dots when it is longer.

    Args:
        value: Any value (typically a dictionary key).
        max_length: The longest text that may be returned, dots included. Meant for
            values of at least 3, because the dots alone take three characters.

    Returns:
        The repr as it is, or its beginning followed by "...".
    """

    # 1. Take the repr of the value
    text = repr(value)

    # 2. A short text is returned as it is
    if len(text) <= max_length:
        return text

    # 3. A long text is cut; the three dots count into the limit
    return text[: max(max_length - 3, 0)] + "..."


_DESIGN_NOTES = """
# shorten_repr — Keep a Label Readable

## Purpose
A dictionary key can be anything hashable — a long string, a tuple of several
values, a frozenset. Written whole into a label it would push the actual
message out of sight. This helper keeps the label to a fixed length.

## Why It Is Safe To Cut
The key in a label only says WHERE the problem is. The offending value (or the
whole key, when the key is what failed) is always carried by the exception
card itself, so nothing needed for diagnosis is lost.

## Details
* The limit includes the three dots, so for a `max_length` of at least 3 the
  result never exceeds it. Below 3 the dots alone are returned.
* The cut text is not closed with a quote or a bracket; the dots mark it as cut.
* A short repr passes through untouched.
"""
