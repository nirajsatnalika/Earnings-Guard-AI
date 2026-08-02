"""Beneish M-Score component formulas — 8 official variables.

Each function computes one of the eight Beneish components from the
ValueStore. The ValueStore provides multi-period values (period 0 = current,
period 1 = prior). Each component returns its value or None when inputs are
missing or a denominator is zero.

Official Beneish M-Score components:
  DSRI  — Days Sales in Receivables Index
  GMI   — Gross Margin Index
  AQI   — Asset Quality Index
  SGI   — Sales Growth Index
  DEPI  — Depreciation Index
  SGAI  — SG&A Expenses Index
  LVGI  — Leverage Index
  TATA  — Total Accruals to Total Assets
"""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import ValueStore, safe_divide, safe_subtract

# ---------------------------------------------------------------------------
# Each component function returns (value, formula_string, inputs_dict, interp)
# ---------------------------------------------------------------------------


def compute_dsri(vs: ValueStore) -> tuple[float | None, str, dict[str, float | None], str]:
    """DSRI = (Receivables_t / Revenue_t) / (Receivables_t-1 / Revenue_t-1).

    Measures whether receivables are growing disproportionately vs. revenue.
    A value > 1 indicates receivables are growing faster than sales.
    """
    recv = vs.get_all("Receivables")
    rev = vs.get_all("Revenue")
    inputs = {
        "Receivables_t": recv[0] if len(recv) >= 1 else None,
        "Revenue_t": rev[0] if len(rev) >= 1 else None,
        "Receivables_t-1": recv[1] if len(recv) >= 2 else None,
        "Revenue_t-1": rev[1] if len(rev) >= 2 else None,
    }
    if len(recv) < 2 or len(rev) < 2:
        return None, _formula("DSRI"), inputs, "Insufficient periods — requires two years of receivables and revenue."

    curr = safe_divide(recv[0], rev[0])
    prev = safe_divide(recv[1], rev[1])
    if curr is None or prev is None:
        return None, _formula("DSRI"), inputs, "Could not compute receivables/revenue ratio — missing values or zero revenue."
    value = safe_divide(curr, prev)
    if value is None:
        return None, _formula("DSRI"), inputs, "Prior-year receivables/revenue ratio is zero — cannot compute index."
    interp = (
        f"Receivables-to-revenue ratio {'increased' if value > 1 else 'decreased'} "
        f"by {(abs(value - 1) * 100):.1f}% vs. prior year."
    )
    return value, _formula("DSRI"), inputs, interp


def compute_gmi(vs: ValueStore) -> tuple[float | None, str, dict[str, float | None], str]:
    """GMI = GrossMargin_t-1 / GrossMargin_t.

    Measures whether gross margin has deteriorated. A value > 1 indicates
    margins are declining, which is associated with earnings manipulation.
    """
    rev = vs.get_all("Revenue")
    gp = vs.get_all("Gross Profit")
    inputs = {
        "Revenue_t": rev[0] if len(rev) >= 1 else None,
        "GrossProfit_t": gp[0] if len(gp) >= 1 else None,
        "Revenue_t-1": rev[1] if len(rev) >= 2 else None,
        "GrossProfit_t-1": gp[1] if len(gp) >= 2 else None,
    }
    if len(rev) < 2 or len(gp) < 2:
        return None, _formula("GMI"), inputs, "Insufficient periods — requires two years of revenue and gross profit."

    margin_curr = safe_divide(gp[0], rev[0])
    margin_prev = safe_divide(gp[1], rev[1])
    if margin_curr is None or margin_prev is None:
        return None, _formula("GMI"), inputs, "Could not compute gross margin — missing values or zero revenue."
    value = safe_divide(margin_prev, margin_curr)
    if value is None:
        return None, _formula("GMI"), inputs, "Current-year gross margin is zero — cannot compute index."
    interp = (
        f"Gross margin {'deteriorated' if value > 1 else 'improved'} "
        f"from {margin_prev * 100:.1f}% to {margin_curr * 100:.1f}%."
    )
    return value, _formula("GMI"), inputs, interp


def compute_aqi(vs: ValueStore) -> tuple[float | None, str, dict[str, float | None], str]:
    """AQI = (1 - (CurrentAssets_t + PPE_t) / TotalAssets_t) /
             (1 - (CurrentAssets_t-1 + PPE_t-1) / TotalAssets_t-1)

    Measures whether the proportion of soft assets (non-current, non-PPE) has
    increased, which can indicate manipulation via asset capitalization.
    """
    ca = vs.get_all("Current Assets")
    ppe = vs.get_all("Property Plant and Equipment")
    ta = vs.get_all("Total Assets")
    inputs = {
        "CurrentAssets_t": ca[0] if len(ca) >= 1 else None,
        "PPE_t": ppe[0] if len(ppe) >= 1 else None,
        "TotalAssets_t": ta[0] if len(ta) >= 1 else None,
        "CurrentAssets_t-1": ca[1] if len(ca) >= 2 else None,
        "PPE_t-1": ppe[1] if len(ppe) >= 2 else None,
        "TotalAssets_t-1": ta[1] if len(ta) >= 2 else None,
    }
    if len(ca) < 2 or len(ppe) < 2 or len(ta) < 2:
        return None, _formula("AQI"), inputs, "Insufficient periods — requires two years of current assets, PPE, and total assets."

    ratio_curr = safe_divide(ca[0] + ppe[0], ta[0])
    ratio_prev = safe_divide(ca[1] + ppe[1], ta[1])
    if ratio_curr is None or ratio_prev is None:
        return None, _formula("AQI"), inputs, "Could not compute asset-quality ratio — missing values or zero total assets."

    curr_soft = 1 - ratio_curr
    prev_soft = 1 - ratio_prev
    value = safe_divide(curr_soft, prev_soft)
    if value is None:
        return None, _formula("AQI"), inputs, "Prior-year soft-asset ratio is zero — cannot compute index."
    interp = (
        f"Proportion of soft assets {'increased' if value > 1 else 'decreased'} "
        f"by {(abs(value - 1) * 100):.1f}% vs. prior year."
    )
    return value, _formula("AQI"), inputs, interp


def compute_sgi(vs: ValueStore) -> tuple[float | None, str, dict[str, float | None], str]:
    """SGI = Revenue_t / Revenue_t-1.

    Measures sales growth. High growth firms are more likely to manipulate
    earnings to sustain growth expectations.
    """
    rev = vs.get_all("Revenue")
    inputs = {
        "Revenue_t": rev[0] if len(rev) >= 1 else None,
        "Revenue_t-1": rev[1] if len(rev) >= 2 else None,
    }
    if len(rev) < 2:
        return None, _formula("SGI"), inputs, "Insufficient periods — requires two years of revenue."
    value = safe_divide(rev[0], rev[1])
    if value is None:
        return None, _formula("SGI"), inputs, "Prior-year revenue is zero — cannot compute growth index."
    interp = f"Revenue grew by {(value - 1) * 100:.1f}% over the prior year."
    return value, _formula("SGI"), inputs, interp


def compute_depi(vs: ValueStore) -> tuple[float | None, str, dict[str, float | None], str]:
    """DEPI = (Depreciation_t-1 / (PPE_t-1 + Depreciation_t-1)) /
             (Depreciation_t   / (PPE_t   + Depreciation_t))

    Measures whether the depreciation rate has slowed, which can indicate
    aggressive useful-life assumptions to inflate assets and earnings.
    """
    dep = vs.get_all("Depreciation")
    ppe = vs.get_all("Property Plant and Equipment")
    inputs = {
        "Depreciation_t": dep[0] if len(dep) >= 1 else None,
        "PPE_t": ppe[0] if len(ppe) >= 1 else None,
        "Depreciation_t-1": dep[1] if len(dep) >= 2 else None,
        "PPE_t-1": ppe[1] if len(ppe) >= 2 else None,
    }
    if len(dep) < 2 or len(ppe) < 2:
        return None, _formula("DEPI"), inputs, "Insufficient periods — requires two years of depreciation and PPE."

    rate_curr = safe_divide(dep[0], ppe[0] + dep[0])
    rate_prev = safe_divide(dep[1], ppe[1] + dep[1])
    if rate_curr is None or rate_prev is None:
        return None, _formula("DEPI"), inputs, "Could not compute depreciation rate — missing values or zero (PPE + depreciation)."
    value = safe_divide(rate_prev, rate_curr)
    if value is None:
        return None, _formula("DEPI"), inputs, "Current-year depreciation rate is zero — cannot compute index."
    interp = (
        f"Depreciation rate {'slowed' if value > 1 else 'accelerated'} "
        f"by {(abs(value - 1) * 100):.1f}% vs. prior year."
    )
    return value, _formula("DEPI"), inputs, interp


def compute_sgai(vs: ValueStore) -> tuple[float | None, str, dict[str, float | None], str]:
    """SGAI = (SGA_t / Revenue_t) / (SGA_t-1 / Revenue_t-1)

    Measures whether SG&A expenses as a proportion of revenue have increased,
    which can indicate manipulation to reduce expenses artificially.
    Uses EBIT - PAT as a proxy for SG&A when SG&A is not directly available.
    """
    rev = vs.get_all("Revenue")
    # Proxy: SG&A ≈ Revenue - EBIT (operating expenses excluding COGS).
    # This is a simplification; the model ideally uses reported SG&A.
    ebit = vs.get_all("EBIT")
    inputs = {
        "Revenue_t": rev[0] if len(rev) >= 1 else None,
        "EBIT_t": ebit[0] if len(ebit) >= 1 else None,
        "Revenue_t-1": rev[1] if len(rev) >= 2 else None,
        "EBIT_t-1": ebit[1] if len(ebit) >= 2 else None,
    }
    if len(rev) < 2 or len(ebit) < 2:
        return None, _formula("SGAI"), inputs, "Insufficient periods — requires two years of revenue and EBIT (SG&A proxy)."

    sga_curr = safe_subtract(rev[0], ebit[0])
    sga_prev = safe_subtract(rev[1], ebit[1])
    if sga_curr is None or sga_prev is None:
        return None, _formula("SGAI"), inputs, "Could not compute SG&A proxy — missing values."
    ratio_curr = safe_divide(sga_curr, rev[0])
    ratio_prev = safe_divide(sga_prev, rev[1])
    if ratio_curr is None or ratio_prev is None:
        return None, _formula("SGAI"), inputs, "Could not compute SG&A-to-revenue ratio — missing values or zero revenue."
    value = safe_divide(ratio_curr, ratio_prev)
    if value is None:
        return None, _formula("SGAI"), inputs, "Prior-year SG&A-to-revenue ratio is zero — cannot compute index."
    interp = (
        f"SG&A-to-revenue ratio {'increased' if value > 1 else 'decreased'} "
        f"by {(abs(value - 1) * 100):.1f}% vs. prior year."
    )
    return value, _formula("SGAI"), inputs, interp


def compute_lvgi(vs: ValueStore) -> tuple[float | None, str, dict[str, float | None], str]:
    """LVGI = (TotalLiabilities_t / TotalAssets_t) /
             (TotalLiabilities_t-1 / TotalAssets_t-1)

    Measures whether leverage has increased, which can indicate pressure to
    manipulate earnings to meet debt covenants.
    """
    tl = vs.get_all("Total Liabilities")
    ta = vs.get_all("Total Assets")
    inputs = {
        "TotalLiabilities_t": tl[0] if len(tl) >= 1 else None,
        "TotalAssets_t": ta[0] if len(ta) >= 1 else None,
        "TotalLiabilities_t-1": tl[1] if len(tl) >= 2 else None,
        "TotalAssets_t-1": ta[1] if len(ta) >= 2 else None,
    }
    if len(tl) < 2 or len(ta) < 2:
        return None, _formula("LVGI"), inputs, "Insufficient periods — requires two years of total liabilities and total assets."

    lev_curr = safe_divide(tl[0], ta[0])
    lev_prev = safe_divide(tl[1], ta[1])
    if lev_curr is None or lev_prev is None:
        return None, _formula("LVGI"), inputs, "Could not compute leverage ratio — missing values or zero total assets."
    value = safe_divide(lev_curr, lev_prev)
    if value is None:
        return None, _formula("LVGI"), inputs, "Prior-year leverage ratio is zero — cannot compute index."
    interp = (
        f"Leverage ratio {'increased' if value > 1 else 'decreased'} "
        f"by {(abs(value - 1) * 100):.1f}% vs. prior year."
    )
    return value, _formula("LVGI"), inputs, interp


def compute_tata(vs: ValueStore) -> tuple[float | None, str, dict[str, float | None], str]:
    """TATA = (PAT_t - CFO_t) / TotalAssets_t

    Measures total accruals relative to total assets. High accruals indicate
    earnings are less backed by cash and more likely manipulated.
    """
    pat = vs.get("PAT")
    cfo = vs.get("Operating Cash Flow")
    ta = vs.get("Total Assets")
    inputs = {
        "PAT_t": pat,
        "CFO_t": cfo,
        "TotalAssets_t": ta,
    }
    if pat is None or cfo is None or ta is None:
        return None, _formula("TATA"), inputs, "Requires PAT, operating cash flow, and total assets for the current period."
    accruals = safe_subtract(pat, cfo)
    if accruals is None:
        return None, _formula("TATA"), inputs, "Could not compute accruals — missing PAT or CFO."
    value = safe_divide(accruals, ta)
    if value is None:
        return None, _formula("TATA"), inputs, "Total assets is zero — cannot compute ratio."
    interp = f"Accruals represent {value * 100:.1f}% of total assets."
    return value, _formula("TATA"), inputs, interp


# ---------------------------------------------------------------------------
# Formula strings
# ---------------------------------------------------------------------------

_FORMULAS = {
    "DSRI": "DSRI = (Receivables_t / Revenue_t) / (Receivables_t-1 / Revenue_t-1)",
    "GMI": "GMI = GrossMargin_t-1 / GrossMargin_t",
    "AQI": "AQI = (1 - (CA_t + PPE_t) / TA_t) / (1 - (CA_t-1 + PPE_t-1) / TA_t-1)",
    "SGI": "SGI = Revenue_t / Revenue_t-1",
    "DEPI": "DEPI = (Dep_t-1 / (PPE_t-1 + Dep_t-1)) / (Dep_t / (PPE_t + Dep_t))",
    "SGAI": "SGAI = (SGA_t / Revenue_t) / (SGA_t-1 / Revenue_t-1)",
    "LVGI": "LVGI = (TL_t / TA_t) / (TL_t-1 / TA_t-1)",
    "TATA": "TATA = (PAT_t - CFO_t) / TA_t",
}


def _formula(name: str) -> str:
    return _FORMULAS.get(name, "")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

COMPONENT_FUNCTIONS = [
    ("DSRI", compute_dsri),
    ("GMI", compute_gmi),
    ("AQI", compute_aqi),
    ("SGI", compute_sgi),
    ("DEPI", compute_depi),
    ("SGAI", compute_sgai),
    ("LVGI", compute_lvgi),
    ("TATA", compute_tata),
]
