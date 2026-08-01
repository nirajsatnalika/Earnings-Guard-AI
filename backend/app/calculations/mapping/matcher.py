"""Mapping utilities — normalization and multi-strategy label matching.

Matching priority (first hit wins):
  1. Exact match against canonical fields
  2. Case-insensitive match
  3. Whitespace-removed match
  4. Punctuation-removed match
  5. Alias dictionary match
  6. Fuzzy match via RapidFuzz (threshold-gated)

Every match returns a confidence score 0–100. Exact / case / space /
punctuation matches score 100. Alias matches score 99. Fuzzy matches
score the RapidFuzz similarity ratio, but only if it meets the threshold.
"""

from __future__ import annotations

import string
import unicodedata

from rapidfuzz import fuzz

from app.calculations.mapping.aliases import ALIASES
from app.calculations.mapping.dictionary import CANONICAL_FIELDS

# Minimum RapidFuzz ratio (0–100) for a fuzzy match to be accepted.
FUZZY_THRESHOLD: int = 85


def _strip_punct(text: str) -> str:
    """Remove punctuation characters from text."""
    return text.translate(str.maketrans("", "", string.punctuation))


# Pre-compute normalized forms of canonical fields for fast lookup.
_CANONICAL_LOWER: dict[str, str] = {field.lower(): field for field in CANONICAL_FIELDS}
_CANONICAL_NO_SPACE: dict[str, str] = {
    field.replace(" ", "").lower(): field for field in CANONICAL_FIELDS
}
_CANONICAL_NO_PUNCT: dict[str, str] = {
    _strip_punct(field).replace(" ", "").lower(): field for field in CANONICAL_FIELDS
}

# Pre-compute normalized alias forms.
_ALIASES_LOWER: dict[str, str] = {alias.lower(): canonical for alias, canonical in ALIASES.items()}
_ALIASES_NO_SPACE: dict[str, str] = {
    alias.replace(" ", "").lower(): canonical for alias, canonical in ALIASES.items()
}
_ALIASES_NO_PUNCT: dict[str, str] = {
    _strip_punct(alias).replace(" ", "").lower(): canonical for alias, canonical in ALIASES.items()
}


def normalize(text: str) -> str:
    """Normalize a raw label: Unicode NFKC + collapse whitespace."""
    if not isinstance(text, str):
        return ""
    return " ".join(unicodedata.normalize("NFKC", text).split())


class MatchResult:
    """Outcome of matching a single raw label."""

    __slots__ = ("canonical", "confidence", "strategy")

    def __init__(self, canonical: str | None, confidence: int, strategy: str) -> None:
        self.canonical = canonical
        self.confidence = confidence
        self.strategy = strategy

    @property
    def matched(self) -> bool:
        return self.canonical is not None


def match_label(raw_label: str) -> MatchResult:
    """Match a raw statement label to a canonical field using the priority strategy."""
    label = normalize(raw_label)
    if not label:
        return MatchResult(None, 0, "empty")

    # 1. Exact match
    if label in CANONICAL_FIELDS:
        return MatchResult(label, 100, "exact")

    # 2. Case-insensitive match
    lower = label.lower()
    if lower in _CANONICAL_LOWER:
        return MatchResult(_CANONICAL_LOWER[lower], 100, "case_insensitive")

    # 3. Whitespace-removed match
    no_space = label.replace(" ", "").lower()
    if no_space in _CANONICAL_NO_SPACE:
        return MatchResult(_CANONICAL_NO_SPACE[no_space], 100, "no_space")

    # 4. Punctuation-removed match
    no_punct = _strip_punct(label).replace(" ", "").lower()
    if no_punct in _CANONICAL_NO_PUNCT:
        return MatchResult(_CANONICAL_NO_PUNCT[no_punct], 100, "no_punctuation")

    # 5. Alias dictionary match (same sub-strategies)
    if lower in _ALIASES_LOWER:
        return MatchResult(_ALIASES_LOWER[lower], 99, "alias")
    if no_space in _ALIASES_NO_SPACE:
        return MatchResult(_ALIASES_NO_SPACE[no_space], 99, "alias_no_space")
    if no_punct in _ALIASES_NO_PUNCT:
        return MatchResult(_ALIASES_NO_PUNCT[no_punct], 99, "alias_no_punctuation")

    # 6. Fuzzy match via RapidFuzz
    best_field: str | None = None
    best_score = 0
    for field in CANONICAL_FIELDS:
        score = int(fuzz.WRatio(label, field))
        if score > best_score:
            best_score = score
            best_field = field

    # Also fuzzy-match against aliases, carrying over the alias's canonical field.
    for alias, canonical in ALIASES.items():
        score = int(fuzz.WRatio(label, alias))
        if score > best_score:
            best_score = score
            best_field = canonical

    if best_field is not None and best_score >= FUZZY_THRESHOLD:
        return MatchResult(best_field, best_score, "fuzzy")

    return MatchResult(None, 0, "unmapped")
