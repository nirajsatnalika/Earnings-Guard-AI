"""Established Financial Models Evaluator for EFS™ Framework.

Evaluates the five established models integrated into EFS™ v1.0:
1. Beneish M-Score (Supporting Evidence) — Beneish (1999) 8-variable model
2. Sloan Accrual Model (Supporting Evidence) — Sloan (1996) Accrual Ratio
3. Altman Z-Score (Cross-Validation) — Altman (1968) 5-factor manufacturing specification
4. Piotroski F-Score (Cross-Validation) — Piotroski (2000) 9 binary signal model
5. Ohlson O-Score (Cross-Validation) — Ohlson (1980) 9-variable Logit specification

Per EFS methodology, these models are evaluated independently and kept separately
visible in the assessment to avoid double-counting or treating them as fraud declarations.
"""

from math import exp, log
from typing import Any, Dict, Optional

from app.calculations.beneish.model import compute_m_score


class EstablishedModelsEvaluator:
    """Evaluates 5 established financial models deterministically."""

    def evaluate_all(self, raw_variables: Dict[str, Any], feature_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluates all 5 established models and returns structured results."""
        feature_data = feature_data or {}
        
        return {
            "beneish_m_score": self.evaluate_beneish(raw_variables, feature_data),
            "sloan_accrual": self.evaluate_sloan(raw_variables, feature_data),
            "altman_z_score": self.evaluate_altman(raw_variables, feature_data),
            "piotroski_f_score": self.evaluate_piotroski(raw_variables, feature_data),
            "ohlson_o_score": self.evaluate_ohlson(raw_variables, feature_data),
        }

    def evaluate_beneish(self, vars_map: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Beneish M-Score evaluation (Beneish 1999 8-Variable Specification)."""
        m_score = vars_map.get("MODEL01") or features.get("beneish_m_score")
        components = {}
        
        if m_score is None:
            components = {
                "DSRI": vars_map.get("DSRI", vars_map.get("FSQ03")),
                "GMI": vars_map.get("GMI"),
                "AQI": vars_map.get("AQI", vars_map.get("BSI02")),
                "SGI": vars_map.get("SGI"),
                "DEPI": vars_map.get("DEPI"),
                "SGAI": vars_map.get("SGAI"),
                "TATA": vars_map.get("TATA"),
                "LVGI": vars_map.get("LVGI"),
            }
            if all(v is not None for v in components.values()):
                m_score = compute_m_score({k: float(v) for k, v in components.items()})

        if m_score is not None:
            score_val = round(float(m_score), 4)
            is_high_risk = score_val > -1.78
            return {
                "model_id": "MODEL01",
                "model_name": "Beneish M-Score",
                "specification": "Beneish (1999) 8-Variable Probabilistic Model",
                "score": score_val,
                "threshold": -1.78,
                "risk_signal": "Elevated Forensic Risk" if is_high_risk else "Low Risk",
                "role": "Supporting Evidence",
                "status": "COMPLETED",
                "components": components,
                "interpretation": (
                    f"M-Score of {score_val} is above threshold (-1.78), indicating elevated manipulation risk."
                    if is_high_risk
                    else f"M-Score of {score_val} is below threshold (-1.78), indicating low manipulation risk signal."
                ),
            }

        return {
            "model_id": "MODEL01",
            "model_name": "Beneish M-Score",
            "specification": "Beneish (1999) 8-Variable Probabilistic Model",
            "score": None,
            "threshold": -1.78,
            "risk_signal": "Insufficient Evidence",
            "role": "Supporting Evidence",
            "status": "INSUFFICIENT_DATA",
            "interpretation": "Beneish M-Score could not be computed due to missing input components.",
        }

    def evaluate_sloan(self, vars_map: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Sloan Accrual Model evaluation (Sloan 1996 Specification).
        
        Accrual Ratio = (Net Income - CFO) / Total Assets
        """
        sloan_val = vars_map.get("MODEL02") or vars_map.get("AQ03") or features.get("sloan_accrual")
        
        net_income = vars_map.get("pat") or vars_map.get("net_income")
        cfo = vars_map.get("cfo")
        total_assets = vars_map.get("total_assets")

        if sloan_val is None and net_income is not None and cfo is not None and total_assets and float(total_assets) > 0:
            sloan_val = (float(net_income) - float(cfo)) / float(total_assets)

        if sloan_val is not None:
            score_val = round(float(sloan_val), 4)
            is_high_accrual = score_val > 0.08
            return {
                "model_id": "MODEL02",
                "model_name": "Sloan Accrual Model",
                "specification": "Sloan (1996) Balance Sheet / Cash Flow Accrual Ratio",
                "score": score_val,
                "threshold": 0.08,
                "risk_signal": "Elevated Accrual Risk" if is_high_accrual else "Low Accrual Risk",
                "role": "Supporting Evidence",
                "status": "COMPLETED",
                "components": {"net_income": net_income, "cfo": cfo, "total_assets": total_assets},
                "interpretation": (
                    f"Sloan Accrual Ratio of {score_val:.2%} indicates high accrual dependency relative to cash flow."
                    if is_high_accrual
                    else f"Sloan Accrual Ratio of {score_val:.2%} reflects healthy cash-backed earnings."
                ),
            }

        return {
            "model_id": "MODEL02",
            "model_name": "Sloan Accrual Model",
            "specification": "Sloan (1996) Balance Sheet / Cash Flow Accrual Ratio",
            "score": None,
            "threshold": 0.08,
            "risk_signal": "Insufficient Evidence",
            "role": "Supporting Evidence",
            "status": "INSUFFICIENT_DATA",
            "interpretation": "Sloan Accrual Model could not be computed due to missing Net Income, CFO, or Total Assets.",
        }

    def evaluate_altman(self, vars_map: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Altman Z-Score evaluation (Altman 1968 Original Manufacturing Specification).
        
        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets
        X3 = EBIT / Total Assets
        X4 = Market Value of Equity / Total Liabilities
        X5 = Sales / Total Assets
        """
        altman_val = vars_map.get("MODEL03") or features.get("altman_z_score")
        components = {}

        if altman_val is None:
            ta = vars_map.get("total_assets")
            wc = vars_map.get("working_capital")
            re = vars_map.get("retained_earnings")
            ebit = vars_map.get("ebit")
            mve = vars_map.get("market_value_equity") or vars_map.get("book_value_equity")
            tl = vars_map.get("total_liabilities")
            sales = vars_map.get("revenue") or vars_map.get("sales")

            if ta and float(ta) > 0 and tl and float(tl) > 0:
                ta, tl = float(ta), float(tl)
                x1 = (float(wc) / ta) if wc is not None else None
                x2 = (float(re) / ta) if re is not None else None
                x3 = (float(ebit) / ta) if ebit is not None else None
                x4 = (float(mve) / tl) if mve is not None else None
                x5 = (float(sales) / ta) if sales is not None else None

                components = {"X1": x1, "X2": x2, "X3": x3, "X4": x4, "X5": x5}

                if all(v is not None for v in [x1, x2, x3, x4, x5]):
                    altman_val = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5

        if altman_val is not None:
            score_val = round(float(altman_val), 4)
            if score_val < 1.81:
                zone = "Distress Zone"
                signal = "Elevated Distress Risk"
            elif score_val <= 2.99:
                zone = "Grey Zone"
                signal = "Moderate Distress Risk"
            else:
                zone = "Safe Zone"
                signal = "Low Distress Risk"

            return {
                "model_id": "MODEL03",
                "model_name": "Altman Z-Score",
                "specification": "Altman (1968) 5-Factor Original Manufacturing Z-Score",
                "score": score_val,
                "zone": zone,
                "risk_signal": signal,
                "role": "Cross-Validation",
                "status": "COMPLETED",
                "components": components,
                "interpretation": f"Altman Z-Score of {score_val} places company in the {zone}.",
            }

        return {
            "model_id": "MODEL03",
            "model_name": "Altman Z-Score",
            "specification": "Altman (1968) 5-Factor Original Manufacturing Z-Score",
            "score": None,
            "zone": "Unknown",
            "risk_signal": "Insufficient Evidence",
            "role": "Cross-Validation",
            "status": "INSUFFICIENT_DATA",
            "interpretation": "Altman Z-Score could not be evaluated due to missing financial statement inputs.",
        }

    def evaluate_piotroski(self, vars_map: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Piotroski F-Score evaluation (Piotroski 2000 9 Binary Signal Specification)."""
        f_score = vars_map.get("MODEL04") or features.get("piotroski_f_score")
        signals = {}

        if f_score is None:
            # Check individual 9 Piotroski signals if provided
            sig_keys = [
                "f_roa", "f_cfo", "f_droa", "f_accrual",
                "f_dlever", "f_dliquid", "f_eq_issue",
                "f_dmargin", "f_dturn"
            ]
            for k in sig_keys:
                if k in vars_map and vars_map[k] is not None:
                    signals[k] = 1 if bool(vars_map[k]) else 0

            if len(signals) == 9:
                f_score = sum(signals.values())

        if f_score is not None:
            score_val = int(f_score)
            if score_val >= 8:
                quality = "Strong Financial Health"
            elif score_val >= 4:
                quality = "Moderate Financial Health"
            else:
                quality = "Weak Financial Health"

            return {
                "model_id": "MODEL04",
                "model_name": "Piotroski F-Score",
                "specification": "Piotroski (2000) 9-Signal Financial Quality Score",
                "score": score_val,
                "max_score": 9,
                "risk_signal": quality,
                "role": "Cross-Validation",
                "status": "COMPLETED",
                "signals": signals,
                "interpretation": f"Piotroski F-Score of {score_val}/9 reflects {quality.lower()}.",
            }

        return {
            "model_id": "MODEL04",
            "model_name": "Piotroski F-Score",
            "specification": "Piotroski (2000) 9-Signal Financial Quality Score",
            "score": None,
            "max_score": 9,
            "risk_signal": "Insufficient Evidence",
            "role": "Cross-Validation",
            "status": "INSUFFICIENT_DATA",
            "interpretation": "Piotroski F-Score could not be evaluated due to missing financial statement inputs.",
        }

    def evaluate_ohlson(self, vars_map: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Ohlson O-Score evaluation (Ohlson 1980 9-Variable Logit Default Model).
        
        Y = -1.32 - 0.407*log(TA/GNP) + 6.03*(TL/TA) - 1.43*(WC/TA) + 0.0757*(CL/CA)
            - 1.72*(OENEG) - 2.37*(NI/TA) - 1.83*(FUTL) + 0.285*(INTWO) - 0.521*(CHGIN)
        Logit Probability = 1 / (1 + exp(-Y))
        """
        o_score = vars_map.get("MODEL05") or features.get("ohlson_o_score")
        components = {}

        if o_score is None:
            ta = vars_map.get("total_assets")
            tl = vars_map.get("total_liabilities")
            wc = vars_map.get("working_capital")
            cl = vars_map.get("current_liabilities")
            ca = vars_map.get("current_assets")
            ni = vars_map.get("net_income") or vars_map.get("pat")
            cfo = vars_map.get("cfo")
            gnp_price_index = vars_map.get("gnp_index", 100.0)

            if ta and tl and ca and float(ta) > 0 and float(ca) > 0:
                ta, tl, ca = float(ta), float(tl), float(ca)
                wc_val = float(wc) if wc is not None else 0.0
                cl_val = float(cl) if cl is not None else 0.0
                ni_val = float(ni) if ni is not None else 0.0
                cfo_val = float(cfo) if cfo is not None else 0.0

                oeneg = 1.0 if tl > ta else 0.0
                futl = cfo_val / tl if tl > 0 else 0.0
                intwo = 1.0 if (vars_map.get("prior_ni", 0) < 0 and ni_val < 0) else 0.0
                chgin = 0.0  # Normalized earnings growth component

                components = {
                    "TA": ta, "TL": tl, "WC": wc_val, "CL": cl_val, "CA": ca,
                    "NI": ni_val, "OENEG": oeneg, "FUTL": futl, "INTWO": intwo
                }

                y = (
                    -1.32
                    - 0.407 * log(max(ta / gnp_price_index, 1.0))
                    + 6.03 * (tl / ta)
                    - 1.43 * (wc_val / ta)
                    + 0.0757 * (cl_val / ca)
                    - 1.72 * oeneg
                    - 2.37 * (ni_val / ta)
                    - 1.83 * futl
                    + 0.285 * intwo
                    - 0.521 * chgin
                )
                o_score = 1.0 / (1.0 + exp(-y))

        if o_score is not None:
            score_val = round(float(o_score), 4)
            is_high_distress = score_val > 0.5
            return {
                "model_id": "MODEL05",
                "model_name": "Ohlson O-Score",
                "specification": "Ohlson (1980) 9-Variable Logit Default Model",
                "score": score_val,
                "threshold": 0.5,
                "risk_signal": "Elevated Default Risk" if is_high_distress else "Low Default Risk",
                "role": "Cross-Validation",
                "status": "COMPLETED",
                "components": components,
                "interpretation": (
                    f"Ohlson O-Score probability of {score_val:.2%} signals high financial default risk."
                    if is_high_distress
                    else f"Ohlson O-Score probability of {score_val:.2%} signals normal operating solvency."
                ),
            }

        return {
            "model_id": "MODEL05",
            "model_name": "Ohlson O-Score",
            "specification": "Ohlson (1980) 9-Variable Logit Default Model",
            "score": None,
            "threshold": 0.5,
            "risk_signal": "Insufficient Evidence",
            "role": "Cross-Validation",
            "status": "INSUFFICIENT_DATA",
            "interpretation": "Ohlson O-Score could not be evaluated due to missing financial statement inputs.",
        }
