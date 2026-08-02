"""Average metrics — period-average values for balance-sheet items.

Requires two periods of data. When only one period is available, the single
value is returned as the average (with a note).
"""

from __future__ import annotations

from app.calculations.features.base import div_zero, make_metric, missing, ok
from app.calculations.ratios.calculation_utils import ValueStore, safe_average

CATEGORY = "averages"


def _average_feature(
    vs: ValueStore,
    canonical: str,
    feature_name: str,
    formula: str,
) -> DerivedMetric:
    periods = vs.get_all(canonical)
    inputs = {
        f"{canonical}_t": periods[0] if len(periods) >= 1 else None,
        f"{canonical}_t-1": periods[1] if len(periods) >= 2 else None,
    }
    if not periods:
        return missing(feature_name, CATEGORY, formula, inputs, f"{canonical} not found in parsed data.")
    if len(periods) >= 2:
        avg = safe_average([periods[0], periods[1]])
        if avg is None:
            return missing(feature_name, CATEGORY, formula, inputs, f"Could not average {canonical} across periods.")
        return ok(
            feature_name, CATEGORY, avg, formula, inputs,
            f"Average of {canonical} across two periods: ({periods[0]:,.0f} + {periods[1]:,.0f}) / 2 = {avg:,.0f}.",
        )
    # Single period — return as-is with note.
    return ok(
        feature_name, CATEGORY, periods[0], formula, inputs,
        f"Only one period available for {canonical} — using single value {periods[0]:,.0f} as average.",
    )


def average_assets(vs: ValueStore) -> DerivedMetric:
    return _average_feature(vs, "Total Assets", "average_assets", "(TotalAssets_t + TotalAssets_t-1) / 2")


def average_inventory(vs: ValueStore) -> DerivedMetric:
    return _average_feature(vs, "Inventory", "average_inventory", "(Inventory_t + Inventory_t-1) / 2")


def average_receivables(vs: ValueStore) -> DerivedMetric:
    return _average_feature(vs, "Receivables", "average_receivables", "(Receivables_t + Receivables_t-1) / 2")


def average_payables(vs: ValueStore) -> DerivedMetric:
    return _average_feature(vs, "Trade Payables", "average_payables", "(TradePayables_t + TradePayables_t-1) / 2")


def average_equity(vs: ValueStore) -> DerivedMetric:
    return _average_feature(vs, "Equity", "average_equity", "(Equity_t + Equity_t-1) / 2")


def average_current_assets(vs: ValueStore) -> DerivedMetric:
    return _average_feature(vs, "Current Assets", "average_current_assets", "(CurrentAssets_t + CurrentAssets_t-1) / 2")


def average_current_liabilities(vs: ValueStore) -> DerivedMetric:
    return _average_feature(vs, "Current Liabilities", "average_current_liabilities", "(CurrentLiabilities_t + CurrentLiabilities_t-1) / 2")


def average_ppe(vs: ValueStore) -> DerivedMetric:
    return _average_feature(vs, "Property Plant and Equipment", "average_ppe", "(PPE_t + PPE_t-1) / 2")


RATIOS = [
    average_assets,
    average_inventory,
    average_receivables,
    average_payables,
    average_equity,
    average_current_assets,
    average_current_liabilities,
    average_ppe,
]
