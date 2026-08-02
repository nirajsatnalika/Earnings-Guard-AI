"""Cash Flow ratios — 15 independent functions.

Measures the relationship between cash flow from operations and other
financial metrics to assess cash generation and sustainability.
"""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import (
    ValueStore,
    interpret_margin,
    interpret_ratio,
    safe_add,
    safe_average,
    safe_divide,
    safe_subtract,
)
from app.schemas.ratios import RatioResult

CATEGORY = "Cash Flow"


def _missing(ratio: str, msg: str = "Required field(s) missing.") -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="missing_input", benchmark="N/A", interpretation=msg)


def _div_zero(ratio: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="division_by_zero", benchmark="N/A", interpretation="Denominator is zero — ratio cannot be computed.")


def _ok(ratio: str, value: float, benchmark: str, interp: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=value, status="computed", benchmark=benchmark, interpretation=interp)


def cfo_to_pat(vs: ValueStore) -> RatioResult:
    cfo, pat = vs.get("Operating Cash Flow"), vs.get("PAT")
    if cfo is None or pat is None:
        return _missing("CFO/PAT")
    value = safe_divide(cfo, pat)
    if value is None:
        return _div_zero("CFO/PAT")
    return _ok("CFO/PAT", value, ">= 1.0", interpret_ratio(value, 1.0, 0.5))


def cfo_to_revenue(vs: ValueStore) -> RatioResult:
    cfo, revenue = vs.get("Operating Cash Flow"), vs.get("Revenue")
    if cfo is None or revenue is None:
        return _missing("CFO/Revenue")
    value = safe_divide(cfo, revenue)
    if value is None:
        return _div_zero("CFO/Revenue")
    return _ok("CFO/Revenue", value, ">= 15%", interpret_margin(value, 15, 5))


def free_cash_flow(vs: ValueStore) -> RatioResult:
    cfo, capex = vs.get("Operating Cash Flow"), vs.get("Property Plant and Equipment")
    if cfo is None or capex is None:
        return _missing("Free Cash Flow")
    value = safe_subtract(cfo, capex)
    if value is None:
        return _missing("Free Cash Flow")
    if value >= 0:
        interp = f"Positive free cash flow ({value:,.0f}) — the business generates cash after investment."
    else:
        interp = f"Negative free cash flow ({value:,.0f}) — capex exceeds operating cash generation."
    return _ok("Free Cash Flow", value, "> 0", interp)


def cash_conversion_ratio(vs: ValueStore) -> RatioResult:
    cfo, pat = vs.get("Operating Cash Flow"), vs.get("PAT")
    if cfo is None or pat is None:
        return _missing("Cash Conversion Ratio")
    value = safe_divide(cfo, pat)
    if value is None:
        return _div_zero("Cash Conversion Ratio")
    return _ok("Cash Conversion Ratio", value, ">= 1.0", interpret_ratio(value, 1.0, 0.5))


def cfo_to_total_assets(vs: ValueStore) -> RatioResult:
    cfo, ta = vs.get("Operating Cash Flow"), vs.get("Total Assets")
    if cfo is None or ta is None:
        return _missing("CFO to Total Assets")
    value = safe_divide(cfo, ta)
    if value is None:
        return _div_zero("CFO to Total Assets")
    return _ok("CFO to Total Assets", value, ">= 10%", interpret_margin(value, 10, 4))


def cfo_to_equity(vs: ValueStore) -> RatioResult:
    cfo, equity = vs.get("Operating Cash Flow"), vs.get("Equity")
    if cfo is None or equity is None:
        return _missing("CFO to Equity")
    value = safe_divide(cfo, equity)
    if value is None:
        return _div_zero("CFO to Equity")
    return _ok("CFO to Equity", value, ">= 15%", interpret_margin(value, 15, 5))


def cfo_to_total_liabilities(vs: ValueStore) -> RatioResult:
    cfo, tl = vs.get("Operating Cash Flow"), vs.get("Total Liabilities")
    if cfo is None or tl is None:
        return _missing("CFO to Total Liabilities")
    value = safe_divide(cfo, tl)
    if value is None:
        return _div_zero("CFO to Total Liabilities")
    return _ok("CFO to Total Liabilities", value, ">= 20%", interpret_margin(value, 20, 8))


def cfo_to_current_liabilities(vs: ValueStore) -> RatioResult:
    cfo, cl = vs.get("Operating Cash Flow"), vs.get("Current Liabilities")
    if cfo is None or cl is None:
        return _missing("CFO to Current Liabilities")
    value = safe_divide(cfo, cl)
    if value is None:
        return _div_zero("CFO to Current Liabilities")
    return _ok("CFO to Current Liabilities", value, ">= 1.0", interpret_ratio(value, 1.0, 0.4))


def cfo_to_finance_cost(vs: ValueStore) -> RatioResult:
    cfo, fc = vs.get("Operating Cash Flow"), vs.get("Finance Cost")
    if cfo is None or fc is None:
        return _missing("CFO to Finance Cost")
    value = safe_divide(cfo, fc)
    if value is None:
        return _div_zero("CFO to Finance Cost")
    return _ok("CFO to Finance Cost", value, ">= 4.0", interpret_ratio(value, 4.0, 2.0))


def fcf_to_revenue(vs: ValueStore) -> RatioResult:
    """Free Cash Flow / Revenue."""
    cfo, capex, revenue = vs.get("Operating Cash Flow"), vs.get("Property Plant and Equipment"), vs.get("Revenue")
    if cfo is None or capex is None or revenue is None:
        return _missing("FCF to Revenue")
    fcf = safe_subtract(cfo, capex)
    if fcf is None:
        return _missing("FCF to Revenue")
    value = safe_divide(fcf, revenue)
    if value is None:
        return _div_zero("FCF to Revenue")
    return _ok("FCF to Revenue", value, ">= 5%", interpret_margin(value, 5, 0))


def fcf_to_equity(vs: ValueStore) -> RatioResult:
    """Free Cash Flow / Equity — cash return to shareholders."""
    cfo, capex, equity = vs.get("Operating Cash Flow"), vs.get("Property Plant and Equipment"), vs.get("Equity")
    if cfo is None or capex is None or equity is None:
        return _missing("FCF to Equity")
    fcf = safe_subtract(cfo, capex)
    if fcf is None:
        return _missing("FCF to Equity")
    value = safe_divide(fcf, equity)
    if value is None:
        return _div_zero("FCF to Equity")
    return _ok("FCF to Equity", value, ">= 10%", interpret_margin(value, 10, 3))


def cfo_to_investing_cash_flow(vs: ValueStore) -> RatioResult:
    """CFO / |CFI| — ability to fund investments from operations."""
    cfo, cfi = vs.get("Operating Cash Flow"), vs.get("Investing Cash Flow")
    if cfo is None or cfi is None:
        return _missing("CFO to Investing Cash Flow")
    denom = abs(cfi) if cfi != 0 else 0.0
    value = safe_divide(cfo, denom)
    if value is None:
        return _div_zero("CFO to Investing Cash Flow")
    return _ok("CFO to Investing Cash Flow", value, ">= 1.0", interpret_ratio(value, 1.0, 0.5))


def capex_to_cfo(vs: ValueStore) -> RatioResult:
    """Capex / CFO — proportion of operating cash spent on investment."""
    capex, cfo = vs.get("Property Plant and Equipment"), vs.get("Operating Cash Flow")
    if capex is None or cfo is None:
        return _missing("Capex to CFO")
    value = safe_divide(capex, cfo)
    if value is None:
        return _div_zero("Capex to CFO")
    return _ok("Capex to CFO", value, "0.20 – 0.50", interpret_ratio(value, 0.3, 0.7, higher_is_better=False))


def cfo_to_average_assets(vs: ValueStore) -> RatioResult:
    """CFO / Average Total Assets (two periods)."""
    cfo = vs.get("Operating Cash Flow")
    ta_periods = vs.get_all("Total Assets")
    if cfo is None or len(ta_periods) < 2:
        return _missing("CFO to Average Assets", "CFO or two periods of Total Assets required.")
    avg_ta = safe_average([ta_periods[0], ta_periods[1]])
    if avg_ta is None:
        return _missing("CFO to Average Assets")
    value = safe_divide(cfo, avg_ta)
    if value is None:
        return _div_zero("CFO to Average Assets")
    return _ok("CFO to Average Assets", value, ">= 10%", interpret_margin(value, 10, 4))


def net_cash_flow_to_revenue(vs: ValueStore) -> RatioResult:
    """(CFO + CFI + CFF) / Revenue — net cash change relative to revenue."""
    cfo, cfi, cff, revenue = vs.get("Operating Cash Flow"), vs.get("Investing Cash Flow"), vs.get("Financing Cash Flow"), vs.get("Revenue")
    if cfo is None or cfi is None or cff is None or revenue is None:
        return _missing("Net Cash Flow to Revenue")
    net_cf = safe_add(safe_add(cfo, cfi), cff)
    if net_cf is None:
        return _missing("Net Cash Flow to Revenue")
    value = safe_divide(net_cf, revenue)
    if value is None:
        return _div_zero("Net Cash Flow to Revenue")
    return _ok("Net Cash Flow to Revenue", value, "> 0%", interpret_margin(value, 5, 0))


RATIOS = [
    cfo_to_pat,
    cfo_to_revenue,
    free_cash_flow,
    cash_conversion_ratio,
    cfo_to_total_assets,
    cfo_to_equity,
    cfo_to_total_liabilities,
    cfo_to_current_liabilities,
    cfo_to_finance_cost,
    fcf_to_revenue,
    fcf_to_equity,
    cfo_to_investing_cash_flow,
    capex_to_cfo,
    cfo_to_average_assets,
    net_cash_flow_to_revenue,
]
