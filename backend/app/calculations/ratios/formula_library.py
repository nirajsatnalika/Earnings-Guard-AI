"""Formula library — registry aggregator for all ratio categories.

This module re-exports the complete list of ratio functions from the
category modules. Each category module lives in ``categories/`` and exposes a
``RATIOS`` list. Adding a new category or ratio only requires editing the
relevant category module — this file stays untouched.
"""

from __future__ import annotations

from app.calculations.ratios.categories import ALL_RATIOS

# Backward-compatible alias — the ratio service imports RATIO_FUNCTIONS.
RATIO_FUNCTIONS: list = ALL_RATIOS
