"""Negative value detection — handles accounting bracket notation.

In financial statements, negative values are often shown in parentheses
(e.g. "(1,234)" means -1234) or with a leading minus sign. This module
detects and converts these conventions to standard negative floats.
"""

from __future__ import annotations

import re

_BRACKET_PATTERN = re.compile(r"^\((.+)\)$")
_MINUS_PATTERN = re.compile(r"^-(.+)$")


def detect_negative(text: str) -> tuple[bool, str]:
    """Detect whether a text value represents a negative number.

    Returns (is_negative, stripped_text) where stripped_text has the
    bracket or minus notation removed.
    """
    if not text:
        return False, text

    text = text.strip()

    bracket_match = _BRACKET_PATTERN.match(text)
    if bracket_match:
        return True, bracket_match.group(1).strip()

    minus_match = _MINUS_PATTERN.match(text)
    if minus_match:
        return True, minus_match.group(1).strip()

    # Trailing minus (some European conventions: "1234-")
    if text.endswith("-") and len(text) > 1:
        return True, text[:-1].strip()

    return False, text
