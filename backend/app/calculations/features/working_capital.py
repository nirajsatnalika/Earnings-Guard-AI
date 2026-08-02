"""Working Capital features — liquidity and capital allocation metrics."""

from __future__ import annotations

from app.calculations.features.base import div_zero, missing, ok
from app.calculations.ratios.calculation_utils import ValueStore, safe_divide, safe_subtract

CATEGORY = "working_capital"


def working_capital(vs: ValueStore) -> DerivedMetric:
    ca, cl = vs.get("Current Assets"), vs.get("Current Liabilities")
    inputs = {"CurrentAssets": ca, "CurrentLiabilities": cl}
    if ca is None or cl is None:
        return missing("working_capital", CATEGORY, "CurrentAssets - CurrentLiabilities", inputs)
    value = safe_subtract(ca, cl)
    if value is None:
        return missing("working_capital", CATEGORY, "CurrentAssets - CurrentLiabilities", inputs)
    interp = f"Working capital of {value:,.0f} — {'positive' if value >= 0 else 'negative'} liquidity buffer."
    return ok("working_capital", CATEGORY, value, "CurrentAssets - CurrentLiabilities", inputs, interp)


def net_working_capital(vs: ValueStore) -> DerivedMetric:
    """NWC = Current Assets - Cash - Current Liabilities (operating working capital)."""
    ca, cash, cl = vs.get("Current Assets"), vs.get("Cash and Cash Equivalents"), vs.get("Current Liabilities")
    inputs = {"CurrentAssets": ca, "Cash": cash, "CurrentLiabilities": cl}
    if ca is None or cash is None or cl is None:
        return missing("net_working_capital", CATEGORY, "CurrentAssets - Cash - CurrentLiabilities", inputs)
    value = safe_subtract(safe_subtract(ca, cash), cl)
    if value is None:
        return missing("net_working_capital", CATEGORY, "CurrentAssets - Cash - CurrentLiabilities", inputs)
    interp = f"Net working capital (ex-cash) of {value:,.0f}."
    return ok("net_working_capital", CATEGORY, value, "CurrentAssets - Cash - CurrentLiabilities", inputs, interp)


def working_capital_to_revenue(vs: ValueStore) -> DerivedMetric:
    ca, cl, rev = vs.get("Current Assets"), vs.get("Current Liabilities"), vs.get("Revenue")
    inputs = {"CurrentAssets": ca, "CurrentLiabilities": cl, "Revenue": rev}
    if ca is None or cl is None or rev is None:
        return missing("wc_to_revenue", CATEGORY, "(CA - CL) / Revenue", inputs)
    nwc = safe_subtract(ca, cl)
    if nwc is None:
        return missing("wc_to_revenue", CATEGORY, "(CA - CL) / Revenue", inputs)
    value = safe_divide(nwc, rev)
    if value is None:
        return div_zero("wc_to_revenue", CATEGORY, "(CA - CL) / Revenue", inputs)
    interp = f"Working capital represents {value * 100:.1f}% of revenue."
    return ok("wc_to_revenue", CATEGORY, value, "(CA - CL) / Revenue", inputs, interp)


def working_capital_to_assets(vs: ValueStore) -> DerivedMetric:
    ca, cl, ta = vs.get("Current Assets"), vs.get("Current Liabilities"), vs.get("Total Assets")
    inputs = {"CurrentAssets": ca, "CurrentLiabilities": cl, "TotalAssets": ta}
    if ca is None or cl is None or ta is None:
        return missing("wc_to_assets", CATEGORY, "(CA - CL) / TotalAssets", inputs)
    nwc = safe_subtract(ca, cl)
    if nwc is None:
        return missing("wc_to_assets", CATEGORY, "(CA - CL) / TotalAssets", inputs)
    value = safe_divide(nwc, ta)
    if value is None:
        return div_zero("wc_to_assets", CATEGORY, "(CA - CL) / TotalAssets", inputs)
    interp = f"Working capital represents {value * 100:.1f}% of total assets."
    return ok("wc_to_assets", CATEGORY, value, "(CA - CL) / TotalAssets", inputs, interp)


def current_liabilities_to_assets(vs: ValueStore) -> DerivedMetric:
    cl, ta = vs.get("Current Liabilities"), vs.get("Total Assets")
    inputs = {"CurrentLiabilities": cl, "TotalAssets": ta}
    if cl is None or ta is None:
        return missing("cl_to_assets", CATEGORY, "CurrentLiabilities / TotalAssets", inputs)
    value = safe_divide(cl, ta)
    if value is None:
        return div_zero("cl_to_assets", CATEGORY, "CurrentLiabilities / TotalAssets", inputs)
    interp = f"Current liabilities are {value * 100:.1f}% of total assets."
    return ok("cl_to_assets", CATEGORY, value, "CurrentLiabilities / TotalAssets", inputs, interp)


RATIOS = [
    working_capital,
    net_working_capital,
    working_capital_to_revenue,
    working_capital_to_assets,
    current_liabilities_to_assets,
]
