"""Unit scaling detection — identifies magnitude qualifiers in financial data.

Financial statements often express values in thousands, millions, or billions.
This module detects these qualifiers from header text, cell annotations, or
column labels and provides the appropriate scale factor.
"""

from __future__ import annotations

import re

# Unit qualifier -> scale factor
UNIT_SCALES: dict[str, float] = {
    "units": 1.0,
    "absolute": 1.0,
    "ones": 1.0,
    "thousands": 1_000.0,
    "thousand": 1_000.0,
    "000s": 1_000.0,
    "k": 1_000.0,
    "k$": 1_000.0,
    "millions": 1_000_000.0,
    "million": 1_000_000.0,
    "mm": 1_000_000.0,
    "m": 1_000_000.0,
    "m$": 1_000_000.0,
    "billions": 1_000_000_000.0,
    "billion": 1_000_000_000.0,
    "bn": 1_000_000_000.0,
    "b": 1_000_000_000.0,
    "b$": 1_000_000_000.0,
    "lakhs": 100_000.0,
    "lakh": 100_000.0,
    "l": 100_000.0,
    "crores": 10_000_000.0,
    "crore": 10_000_000.0,
    "cr": 10_000_000.0,
}

# Ordered patterns for detection (longest first to avoid partial matches)
_UNIT_PATTERNS: list[tuple[re.Pattern[str], str, float]] = [
    (re.compile(r"\b(in\s+)?billions?\b", re.IGNORECASE), "billions", 1_000_000_000.0),
    (re.compile(r"\b(in\s+)?millions?\b", re.IGNORECASE), "millions", 1_000_000.0),
    (re.compile(r"\b(in\s+)?thousands?\b", re.IGNORECASE), "thousands", 1_000.0),
    (re.compile(r"\b(in\s+)?crores?\b", re.IGNORECASE), "crores", 10_000_000.0),
    (re.compile(r"\b(in\s+)?lakhs?\b", re.IGNORECASE), "lakhs", 100_000.0),
    (re.compile(r"\bin\s+units?\b", re.IGNORECASE), "units", 1.0),
    (re.compile(r"\b(in\s+)?absolute\b", re.IGNORECASE), "absolute", 1.0),
    (re.compile(r"\b(in\s+)?000s?\b", re.IGNORECASE), "000s", 1_000.0),
    (re.compile(r"\b(in\s+)?MM\b"), "MM", 1_000_000.0),
    (re.compile(r"\b(in\s+)?Bn\b"), "Bn", 1_000_000_000.0),
    (re.compile(r"\b(in\s+)?Cr\b"), "Cr", 10_000_000.0),
]


def detect_unit(text: str) -> tuple[str | None, float]:
    """Detect the unit scale from a text string.

    Returns (unit_name, scale_factor). If no unit is detected, returns
    (None, 1.0).
    """
    if not text:
        return None, 1.0

    for pattern, name, scale in _UNIT_PATTERNS:
        if pattern.search(text):
            return name, scale

    return None, 1.0


def strip_unit_qualifiers(text: str) -> str:
    """Remove unit qualifier words from a text string."""
    result = text
    for pattern, _, _ in _UNIT_PATTERNS:
        result = pattern.sub("", result)
    return result.strip()
