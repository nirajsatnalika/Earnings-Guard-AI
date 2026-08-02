"""Cash Flow features — free cash flow and cash conversion metrics."""

from __future__ import annotations

from app.calculations.features.base import div_zero, missing, ok
from app.calculations.ratios.calculation_utils import (
    ValueStore,
    safe_average,
    safe_divide,
    safe_subtract,
)

CATEGORY = "cash_flow"


def free_cash_flow(vs: ValueStore) -> DerivedMetric:
    """FCF = CFO - Capex (PPE as capex proxy)."""
    cfo, capex = vs.get("Operating Cash Flow"), vs.get("Property Plant and Equipment")
    inputs = {"CFO": cfo, "Capex": capex}
    if cfo is None or capex is None:
        return missing("free_cash_flow", CATEGORY, "CFO - Capex", inputs)
    value = safe_subtract(cfo, capex)
    if value is None:
        return missing("free_cash_flow", CATEGORY, "CFO - Capex", inputs)
    interp = f"Free cash flow of {value:,.0f} — {'positive' if value >= 0 else 'negative'} FCF."
    return ok("free_cash_flow", CATEGORY, value, "CFO - Capex", inputs, interp)


def fcf_to_revenue(vs: ValueStore) -> DerivedMetric:
    """FCF / Revenue — cash conversion efficiency."""
    cfo, capex, rev = vs.get("Operating Cash Flow"), vs.get("Property Plant and Equipment"), vs.get("Revenue")
    inputs = {"CFO": cfo, "Capex": capex, "Revenue": rev}
    if cfo is None or capex is None or rev is None:
        return missing("fcf_to_revenue", CATEGORY, "(CFO - Capex) / Revenue", inputs)
    fcf = safe_subtract(cfo, capex)
    if fcf is None:
        return missing("fcf_to_revenue", CATEGORY, "(CFO - Capex) / Revenue", inputs)
    value = safe_divide(fcf, rev)
    if value is None:
        return div_zero("fcf_to_revenue", CATEGORY, "(CFO - Capex) / Revenue", inputs)
    interp = f"FCF margin of {value * 100:.1f}%."
    return ok("fcf_to_revenue", CATEGORY, value, "(CFO - Capex) / Revenue", inputs, interp)


def fcf_to_equity(vs: ValueStore) -> DerivedMetric:
    """FCF / Equity — cash return to shareholders."""
    cfo, capex, equity = vs.get("Operating Cash Flow"), vs.get("Property Plant and Equipment"), vs.get("Equity")
    inputs = {"CFO": cfo, "Capex": capex, "Equity": equity}
    if cfo is None or capex is None or equity is None:
        return missing("fcf_to_equity", CATEGORY, "(CFO - Capex) / Equity", inputs)
    fcf = safe_subtract(cfo, capex)
    if fcf is None:
        return missing("fcf_to_equity", CATEGORY, "(CFO - Capex) / Equity", inputs)
    value = safe_divide(fcf, equity)
    if value is None:
        return div_zero("fcf_to_equity", CATEGORY, "(CFO - Capex) / Equity", inputs)
    interp = f"FCF return on equity of {value * 100:.1f}%."
    return ok("fcf_to_equity", CATEGORY, value, "(CFO - Capex) / Equity", inputs, interp)


def fcf_to_noa(vs: ValueStore) -> DerivedMetric:
    """FCF / NOA — free cash flow return on net operating assets."""
    cfo, capex = vs.get("Operating Cash Flow"), vs.get("Property Plant and Equipment")
    ta, cash = vs.get("Total Assets"), vs.get("Cash and Cash Equivalents")
    tl, fc = vs.get("Total Liabilities"), vs.get("Finance Cost")
    inputs = {"CFO": cfo, "Capex": capex, "TotalAssets": ta, "Cash": cash, "TotalLiabilities": tl, "FinanceCost": fc}
    if cfo is None or capex is None or ta is None or cash is None or tl is None:
        return missing("fcf_to_noa", CATEGORY, "(CFO - Capex) / NOA", inputs)
    fc_val = fc if fc is not None else 0.0
    noa_val = safe_subtract(safe_subtract(ta, cash), safe_subtract(tl, fc_val))
    if noa_val is None:
        return missing("fcf_to_noa", CATEGORY, "(CFO - Capex) / NOA", inputs)
    fcf = safe_subtract(cfo, capex)
    if fcf is None:
        return missing("fcf_to_noa", CATEGORY, "(CFO - Capex) / NOA", inputs)
    value = safe_divide(fcf, noa_val)
    if value is None:
        return div_zero("fcf_to_noa", CATEGORY, "(CFO - Capex) / NOA", inputs)
    interp = f"FCF return on net operating assets of {value * 100:.1f}%."
    return ok("fcf_to_noa", CATEGORY, value, "(CFO - Capex) / NOA", inputs, interp)


def cash_conversion_efficiency(vs: ValueStore) -> DerivedMetric:
    """CFO / PAT — how effectively profit converts to cash."""
    cfo, pat = vs.get("Operating Cash Flow"), vs.get("PAT")
    inputs = {"CFO": cfo, "PAT": pat}
    if cfo is None or pat is None:
        return missing("cash_conversion_efficiency", CATEGORY, "CFO / PAT", inputs)
    value = safe_divide(cfo, pat)
    if value is None:
        return div_zero("cash_conversion_efficiency", CATEGORY, "CFO / PAT", inputs)
    interp = f"CFO is {value:.2f}x PAT — {'strong' if value >= 1.0 else 'weak'} cash conversion."
    return ok("cash_conversion_efficiency", CATEGORY, value, "CFO / PAT", inputs, interp)


def capex_ratio(vs: ValueStore) -> DerivedMetric:
    """Capex / Revenue — investment intensity."""
    capex, rev = vs.get("Property Plant and Equipment"), vs.get("Revenue")
    inputs = {"Capex": capex, "Revenue": rev}
    if capex is None or rev is None:
        return missing("capex_ratio", CATEGORY, "Capex / Revenue", inputs)
    value = safe_divide(capex, rev)
    if value is None:
        return div_zero("capex_ratio", CATEGORY, "Capex / Revenue", inputs)
    interp = f"Capex is {value * 100:.1f}% of revenue."
    return ok("capex_ratio", CATEGORY, value, "Capex / Revenue", inputs, interp)


RATIOS = [
    free_cash_flow,
    fcf_to_revenue,
    fcf_to_equity,
    fcf_to_noa,
    cash_conversion_efficiency,
    capex_ratio,
]
