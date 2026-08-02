"""Profitability ratios — 15 independent functions.

Measures a company's ability to generate profit relative to revenue, assets,
equity, and capital employed.
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
    safe_sum,
)
from app.schemas.ratios import RatioResult

CATEGORY = "Profitability"


def _missing(ratio: str, msg: str = "Required field(s) missing.") -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="missing_input", benchmark="N/A", interpretation=msg)


def _div_zero(ratio: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="division_by_zero", benchmark="N/A", interpretation="Denominator is zero — ratio cannot be computed.")


def _ok(ratio: str, value: float, benchmark: str, interp: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=value, status="computed", benchmark=benchmark, interpretation=interp)


def gross_margin(vs: ValueStore) -> RatioResult:
    revenue, gp = vs.get("Revenue"), vs.get("Gross Profit")
    if revenue is None or gp is None:
        return _missing("Gross Margin", "Revenue or Gross Profit missing.")
    value = safe_divide(gp, revenue)
    if value is None:
        return _div_zero("Gross Margin")
    return _ok("Gross Margin", value, "30% – 50%", interpret_margin(value, 30, 10))


def operating_margin(vs: ValueStore) -> RatioResult:
    revenue, ebit = vs.get("Revenue"), vs.get("EBIT")
    if revenue is None or ebit is None:
        return _missing("Operating Margin")
    value = safe_divide(ebit, revenue)
    if value is None:
        return _div_zero("Operating Margin")
    return _ok("Operating Margin", value, "15% – 25%", interpret_margin(value, 15, 5))


def net_margin(vs: ValueStore) -> RatioResult:
    revenue, pat = vs.get("Revenue"), vs.get("PAT")
    if revenue is None or pat is None:
        return _missing("Net Margin")
    value = safe_divide(pat, revenue)
    if value is None:
        return _div_zero("Net Margin")
    return _ok("Net Margin", value, "10% – 20%", interpret_margin(value, 10, 3))


def return_on_assets(vs: ValueStore) -> RatioResult:
    pat, ta = vs.get("PAT"), vs.get("Total Assets")
    if pat is None or ta is None:
        return _missing("ROA")
    value = safe_divide(pat, ta)
    if value is None:
        return _div_zero("ROA")
    return _ok("ROA", value, ">= 7%", interpret_margin(value, 7, 2))


def return_on_equity(vs: ValueStore) -> RatioResult:
    pat, equity = vs.get("PAT"), vs.get("Equity")
    if pat is None or equity is None:
        return _missing("ROE")
    value = safe_divide(pat, equity)
    if value is None:
        return _div_zero("ROE")
    return _ok("ROE", value, ">= 15%", interpret_margin(value, 15, 5))


def return_on_capital_employed(vs: ValueStore) -> RatioResult:
    ebit, ta, cl = vs.get("EBIT"), vs.get("Total Assets"), vs.get("Current Liabilities")
    if ebit is None or ta is None or cl is None:
        return _missing("ROCE")
    ce = safe_subtract(ta, cl)
    if ce is None:
        return _missing("ROCE")
    value = safe_divide(ebit, ce)
    if value is None:
        return _div_zero("ROCE")
    return _ok("ROCE", value, ">= 12%", interpret_margin(value, 12, 5))


def ebitda_margin(vs: ValueStore) -> RatioResult:
    revenue, ebitda = vs.get("Revenue"), vs.get("EBITDA")
    if revenue is None or ebitda is None:
        return _missing("EBITDA Margin", "Revenue or EBITDA missing.")
    value = safe_divide(ebitda, revenue)
    if value is None:
        return _div_zero("EBITDA Margin")
    return _ok("EBITDA Margin", value, ">= 20%", interpret_margin(value, 20, 8))


def return_on_invested_capital(vs: ValueStore) -> RatioResult:
    """ROIC = EBIT / (Equity + Total Liabilities - Current Liabilities)."""
    ebit = vs.get("EBIT")
    equity, tl, cl = vs.get("Equity"), vs.get("Total Liabilities"), vs.get("Current Liabilities")
    if ebit is None or equity is None or tl is None or cl is None:
        return _missing("ROIC")
    invested_capital = safe_subtract(safe_add(equity, tl), cl)
    if invested_capital is None:
        return _missing("ROIC")
    value = safe_divide(ebit, invested_capital)
    if value is None:
        return _div_zero("ROIC")
    return _ok("ROIC", value, ">= 10%", interpret_margin(value, 10, 4))


def return_on_non_current_assets(vs: ValueStore) -> RatioResult:
    ebit, nca = vs.get("EBIT"), vs.get("Non Current Assets")
    if ebit is None or nca is None:
        return _missing("Return on Non-Current Assets")
    value = safe_divide(ebit, nca)
    if value is None:
        return _div_zero("Return on Non-Current Assets")
    return _ok("Return on Non-Current Assets", value, ">= 12%", interpret_margin(value, 12, 5))


def operating_expense_ratio(vs: ValueStore) -> RatioResult:
    """Operating expenses / Revenue (proxy: Revenue - EBIT) / Revenue."""
    revenue, ebit = vs.get("Revenue"), vs.get("EBIT")
    if revenue is None or ebit is None:
        return _missing("Operating Expense Ratio")
    opex = safe_subtract(revenue, ebit)
    if opex is None:
        return _missing("Operating Expense Ratio")
    value = safe_divide(opex, revenue)
    if value is None:
        return _div_zero("Operating Expense Ratio")
    return _ok("Operating Expense Ratio", value, "<= 60%", interpret_ratio(value, 0.4, 0.6, higher_is_better=False))


def interest_burden_ratio(vs: ValueStore) -> RatioResult:
    """PAT / EBIT — measures how much profit remains after interest."""
    pat, ebit = vs.get("PAT"), vs.get("EBIT")
    if pat is None or ebit is None:
        return _missing("Interest Burden Ratio")
    value = safe_divide(pat, ebit)
    if value is None:
        return _div_zero("Interest Burden Ratio")
    return _ok("Interest Burden Ratio", value, ">= 0.70", interpret_ratio(value, 0.7, 0.4))


def tax_burden_ratio(vs: ValueStore) -> RatioResult:
    """PAT / (EBIT - Finance Cost) — profit retained after tax."""
    pat, ebit, fc = vs.get("PAT"), vs.get("EBIT"), vs.get("Finance Cost")
    if pat is None or ebit is None:
        return _missing("Tax Burden Ratio")
    fc_val = fc if fc is not None else 0.0
    pretax = safe_subtract(ebit, fc_val)
    if pretax is None:
        return _missing("Tax Burden Ratio")
    value = safe_divide(pat, pretax)
    if value is None:
        return _div_zero("Tax Burden Ratio")
    return _ok("Tax Burden Ratio", value, ">= 0.70", interpret_ratio(value, 0.7, 0.5))


def ebit_to_total_assets(vs: ValueStore) -> RatioResult:
    ebit, ta = vs.get("EBIT"), vs.get("Total Assets")
    if ebit is None or ta is None:
        return _missing("EBIT to Total Assets")
    value = safe_divide(ebit, ta)
    if value is None:
        return _div_zero("EBIT to Total Assets")
    return _ok("EBIT to Total Assets", value, ">= 10%", interpret_margin(value, 10, 4))


def pat_to_total_liabilities(vs: ValueStore) -> RatioResult:
    pat, tl = vs.get("PAT"), vs.get("Total Liabilities")
    if pat is None or tl is None:
        return _missing("PAT to Total Liabilities")
    value = safe_divide(pat, tl)
    if value is None:
        return _div_zero("PAT to Total Liabilities")
    return _ok("PAT to Total Liabilities", value, ">= 15%", interpret_margin(value, 15, 5))


def return_on_average_assets(vs: ValueStore) -> RatioResult:
    """ROA using average total assets across periods."""
    pat = vs.get("PAT")
    ta_periods = vs.get_all("Total Assets")
    if pat is None or len(ta_periods) < 2:
        return _missing("Return on Average Assets", "PAT or two periods of Total Assets required.")
    avg_ta = safe_average([ta_periods[0], ta_periods[1]])
    if avg_ta is None:
        return _missing("Return on Average Assets")
    value = safe_divide(pat, avg_ta)
    if value is None:
        return _div_zero("Return on Average Assets")
    return _ok("Return on Average Assets", value, ">= 7%", interpret_margin(value, 7, 2))


RATIOS = [
    gross_margin,
    operating_margin,
    net_margin,
    return_on_assets,
    return_on_equity,
    return_on_capital_employed,
    ebitda_margin,
    return_on_invested_capital,
    return_on_non_current_assets,
    operating_expense_ratio,
    interest_burden_ratio,
    tax_burden_ratio,
    ebit_to_total_assets,
    pat_to_total_liabilities,
    return_on_average_assets,
]
