"""Accrual features — earnings quality and NOA metrics.

Net Operating Assets (NOA) = Operating Assets - Operating Liabilities
  Operating Assets = Total Assets - Cash - Marketable Securities
  Operating Liabilities = Total Liabilities - Short-term Debt - Long-term Debt

Total Accruals = PAT - CFO (Sloan accruals)
Accruals Ratio = Total Accruals / Average Total Assets
"""

from __future__ import annotations

from app.calculations.features.base import div_zero, missing, ok
from app.calculations.ratios.calculation_utils import (
    ValueStore,
    safe_average,
    safe_divide,
    safe_subtract,
)

CATEGORY = "accruals"


def noa(vs: ValueStore) -> DerivedMetric:
    """Net Operating Assets = (TotalAssets - Cash) - (TotalLiabilities - FinanceCost).

    Simplified: NOA = TotalAssets - Cash - TotalLiabilities + FinanceCost
    (FinanceCost proxies for interest-bearing debt).
    """
    ta, cash = vs.get("Total Assets"), vs.get("Cash and Cash Equivalents")
    tl, fc = vs.get("Total Liabilities"), vs.get("Finance Cost")
    inputs = {"TotalAssets": ta, "Cash": cash, "TotalLiabilities": tl, "FinanceCost": fc}
    if ta is None or cash is None or tl is None:
        return missing("noa", CATEGORY, "(TA - Cash) - (TL - FinanceCost)", inputs)
    fc_val = fc if fc is not None else 0.0
    op_assets = safe_subtract(ta, cash)
    op_liab = safe_subtract(tl, fc_val)
    if op_assets is None or op_liab is None:
        return missing("noa", CATEGORY, "(TA - Cash) - (TL - FinanceCost)", inputs)
    value = safe_subtract(op_assets, op_liab)
    if value is None:
        return missing("noa", CATEGORY, "(TA - Cash) - (TL - FinanceCost)", inputs)
    interp = f"Net operating assets of {value:,.0f} — capital invested in operations."
    return ok("noa", CATEGORY, value, "(TA - Cash) - (TL - FinanceCost)", inputs, interp)


def noa_growth(vs: ValueStore) -> DerivedMetric:
    """NOA growth = (NOA_t - NOA_t-1) / NOA_t-1.

    Requires two periods of NOA-relevant fields.
    """
    ta = vs.get_all("Total Assets")
    cash = vs.get_all("Cash and Cash Equivalents")
    tl = vs.get_all("Total Liabilities")
    fc = vs.get_all("Finance Cost")
    inputs = {
        "TotalAssets_t": ta[0] if len(ta) >= 1 else None,
        "TotalAssets_t-1": ta[1] if len(ta) >= 2 else None,
        "Cash_t": cash[0] if len(cash) >= 1 else None,
        "Cash_t-1": cash[1] if len(cash) >= 2 else None,
        "TotalLiabilities_t": tl[0] if len(tl) >= 1 else None,
        "TotalLiabilities_t-1": tl[1] if len(tl) >= 2 else None,
    }
    if len(ta) < 2 or len(cash) < 2 or len(tl) < 2:
        return missing("noa_growth", CATEGORY, "(NOA_t - NOA_t-1) / NOA_t-1", inputs, "Two periods required for NOA growth.")
    fc_t = fc[0] if len(fc) >= 1 else 0.0
    fc_prev = fc[1] if len(fc) >= 2 else 0.0
    noa_t = safe_subtract(safe_subtract(ta[0], cash[0]), safe_subtract(tl[0], fc_t))
    noa_prev = safe_subtract(safe_subtract(ta[1], cash[1]), safe_subtract(tl[1], fc_prev))
    if noa_t is None or noa_prev is None:
        return missing("noa_growth", CATEGORY, "(NOA_t - NOA_t-1) / NOA_t-1", inputs)
    value = safe_divide(safe_subtract(noa_t, noa_prev), noa_prev)
    if value is None:
        return div_zero("noa_growth", CATEGORY, "(NOA_t - NOA_t-1) / NOA_t-1", inputs)
    interp = f"NOA {'grew' if value > 0 else 'declined'} by {abs(value) * 100:.1f}% over the prior year."
    return ok("noa_growth", CATEGORY, value, "(NOA_t - NOA_t-1) / NOA_t-1", inputs, interp)


def total_accruals(vs: ValueStore) -> DerivedMetric:
    """Total Accruals = PAT - CFO (Sloan accruals)."""
    pat, cfo = vs.get("PAT"), vs.get("Operating Cash Flow")
    inputs = {"PAT": pat, "CFO": cfo}
    if pat is None or cfo is None:
        return missing("total_accruals", CATEGORY, "PAT - CFO", inputs)
    value = safe_subtract(pat, cfo)
    if value is None:
        return missing("total_accruals", CATEGORY, "PAT - CFO", inputs)
    interp = f"Total accruals of {value:,.0f} — {'positive' if value > 0 else 'negative'} accruals."
    return ok("total_accruals", CATEGORY, value, "PAT - CFO", inputs, interp)


def accruals_ratio(vs: ValueStore) -> DerivedMetric:
    """Accruals Ratio = (PAT - CFO) / Average Total Assets."""
    pat, cfo = vs.get("PAT"), vs.get("Operating Cash Flow")
    ta_periods = vs.get_all("Total Assets")
    inputs = {
        "PAT": pat,
        "CFO": cfo,
        "TotalAssets_t": ta_periods[0] if len(ta_periods) >= 1 else None,
        "TotalAssets_t-1": ta_periods[1] if len(ta_periods) >= 2 else None,
    }
    if pat is None or cfo is None:
        return missing("accruals_ratio", CATEGORY, "(PAT - CFO) / Avg(TotalAssets)", inputs)
    if len(ta_periods) >= 2:
        avg_ta = safe_average([ta_periods[0], ta_periods[1]])
    else:
        avg_ta = ta_periods[0] if ta_periods else None
    if avg_ta is None:
        return missing("accruals_ratio", CATEGORY, "(PAT - CFO) / Avg(TotalAssets)", inputs, "Total Assets required.")
    accruals = safe_subtract(pat, cfo)
    if accruals is None:
        return missing("accruals_ratio", CATEGORY, "(PAT - CFO) / Avg(TotalAssets)", inputs)
    value = safe_divide(accruals, avg_ta)
    if value is None:
        return div_zero("accruals_ratio", CATEGORY, "(PAT - CFO) / Avg(TotalAssets)", inputs)
    interp = f"Accruals are {value * 100:.1f}% of average total assets — {'high' if abs(value) > 0.05 else 'low'} earnings quality signal."
    return ok("accruals_ratio", CATEGORY, value, "(PAT - CFO) / Avg(TotalAssets)", inputs, interp)


def accruals_to_noa(vs: ValueStore) -> DerivedMetric:
    """Accruals / NOA — accruals relative to net operating assets."""
    pat, cfo = vs.get("PAT"), vs.get("Operating Cash Flow")
    ta, cash = vs.get("Total Assets"), vs.get("Cash and Cash Equivalents")
    tl, fc = vs.get("Total Liabilities"), vs.get("Finance Cost")
    inputs = {"PAT": pat, "CFO": cfo, "TotalAssets": ta, "Cash": cash, "TotalLiabilities": tl, "FinanceCost": fc}
    if pat is None or cfo is None or ta is None or cash is None or tl is None:
        return missing("accruals_to_noa", CATEGORY, "(PAT - CFO) / NOA", inputs)
    fc_val = fc if fc is not None else 0.0
    noa_val = safe_subtract(safe_subtract(ta, cash), safe_subtract(tl, fc_val))
    if noa_val is None:
        return missing("accruals_to_noa", CATEGORY, "(PAT - CFO) / NOA", inputs)
    accruals = safe_subtract(pat, cfo)
    if accruals is None:
        return missing("accruals_to_noa", CATEGORY, "(PAT - CFO) / NOA", inputs)
    value = safe_divide(accruals, noa_val)
    if value is None:
        return div_zero("accruals_to_noa", CATEGORY, "(PAT - CFO) / NOA", inputs)
    interp = f"Accruals represent {value * 100:.1f}% of net operating assets."
    return ok("accruals_to_noa", CATEGORY, value, "(PAT - CFO) / NOA", inputs, interp)


RATIOS = [
    noa,
    noa_growth,
    total_accruals,
    accruals_ratio,
    accruals_to_noa,
]
