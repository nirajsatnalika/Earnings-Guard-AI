"""Variable Calculation Engine for EFS™ Framework.

Calculates raw values, data status, unit, and source field traceability for all 95 frozen
EFS variables dynamically loaded from the methodology configuration (efs_variables.json).
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.calculations.efs.models.domain import MethodologyConfig

logger = logging.getLogger(__name__)


class VariableCalculationEngine:
    """Computes all 95 EFS variables deterministically from input financial data."""

    def compute_variables(
        self,
        input_data: Dict[str, Any],
        methodology: MethodologyConfig,
    ) -> Dict[str, Dict[str, Any]]:
        """Computes all registered EFS variables and returns a dict mapping variable_id -> result dict."""
        raw_inputs = input_data.get("raw_variables", {})
        ratio_inputs = input_data.get("ratio_output", {}).get("ratios", {}) if isinstance(input_data.get("ratio_output"), dict) else {}
        feature_inputs = input_data.get("feature_output", {}).get("dataset", {}) if isinstance(input_data.get("feature_output"), dict) else {}
        
        # Merge all incoming data maps
        merged_inputs = {}
        if isinstance(raw_inputs, dict):
            merged_inputs.update(raw_inputs)
        if isinstance(ratio_inputs, dict):
            merged_inputs.update(ratio_inputs)
        if isinstance(feature_inputs, dict):
            merged_inputs.update(feature_inputs)

        var_defs = methodology.registered_variables_definitions if hasattr(methodology, "registered_variables_definitions") else {}
        if not var_defs and hasattr(methodology, "raw_config"):
            var_defs = methodology.raw_config.get("variable_definitions", {})

        computed_results = {}

        for p_name, var_ids in methodology.registered_variables.items():
            for var_id in var_ids:
                def_info = var_defs.get(var_id, {})
                var_name = def_info.get("variable_name", var_id)
                unit = def_info.get("unit", "Ratio")
                pillar_name = def_info.get("pillar", p_name)
                
                raw_val, data_status, source_fields = self._resolve_variable_value(
                    var_id, var_name, merged_inputs, def_info
                )

                computed_results[var_id] = {
                    "variable_id": var_id,
                    "variable_name": var_name,
                    "pillar": pillar_name,
                    "raw_value": raw_val,
                    "unit": unit,
                    "score": None,  # Computed subsequently by ScoringEngine
                    "scoring_band": None,
                    "data_status": data_status,
                    "source_fields": source_fields,
                    "calculation_status": "COMPLETED" if data_status == "AVAILABLE" else "INCOMPLETE",
                }

        logger.info("Variable calculation engine evaluated %d variables.", len(computed_results))
        return computed_results

    def _resolve_variable_value(
        self,
        var_id: str,
        var_name: str,
        inputs: Dict[str, Any],
        def_info: Dict[str, Any],
    ) -> Tuple[Optional[float], str, List[str]]:
        """Resolves variable raw value and sources from inputs."""
        # 1. Direct lookup by var_id
        if var_id in inputs and inputs[var_id] is not None:
            try:
                return float(inputs[var_id]), "AVAILABLE", [var_id.lower()]
            except (ValueError, TypeError):
                pass

        # 2. Lookup by variable_name / snake_case
        snake_name = var_name.lower().replace(" ", "_").replace("&", "and").replace("-", "_").replace("/", "_per_")
        if snake_name in inputs and inputs[snake_name] is not None:
            try:
                return float(inputs[snake_name]), "AVAILABLE", [snake_name]
            except (ValueError, TypeError):
                pass

        # 3. Known formula resolution fallback rules
        resolved_val, sources = self._compute_formula_fallback(var_id, inputs)
        if resolved_val is not None:
            return round(resolved_val, 6), "AVAILABLE", sources

        # If data missing: return explicit MISSING status without defaulting to 0
        return None, "MISSING", [var_id.lower()]

    def _compute_formula_fallback(
        self, var_id: str, inputs: Dict[str, Any]
    ) -> Tuple[Optional[float], List[str]]:
        """Provides deterministic formula fallback calculations for core variables."""
        # Helper to get float from inputs
        def g(key: str) -> Optional[float]:
            val = inputs.get(key)
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None
            return None

        rev = g("revenue") or g("sales")
        prior_rev = g("prior_revenue") or g("prior_sales")
        ar = g("receivables") or g("accounts_receivable")
        prior_ar = g("prior_receivables") or g("prior_accounts_receivable")
        cfo = g("cfo") or g("cash_flow_operations")
        pat = g("pat") or g("net_income")
        cogs = g("cogs") or g("cost_of_goods_sold")
        inv = g("inventory")
        prior_inv = g("prior_inventory")
        ap = g("payables") or g("accounts_payable")
        prior_ap = g("prior_payables")
        total_assets = g("total_assets")
        prior_assets = g("prior_total_assets")

        # FSQ01: Revenue Growth
        if var_id == "FSQ01" and rev and prior_rev and prior_rev > 0:
            return (rev - prior_rev) / prior_rev, ["revenue", "prior_revenue"]

        # FSQ02: AR Growth vs Revenue Growth (Gap)
        if var_id == "FSQ02" and rev and prior_rev and prior_rev > 0 and ar and prior_ar and prior_ar > 0:
            rev_growth = (rev - prior_rev) / prior_rev
            ar_growth = (ar - prior_ar) / prior_ar
            return (ar_growth - rev_growth) * 100, ["accounts_receivable", "revenue"]

        # FSQ03: DSRI
        if var_id == "FSQ03" and rev and prior_rev and prior_rev > 0 and ar and prior_ar and prior_ar > 0:
            dsri = (ar / rev) / (prior_ar / prior_rev)
            return dsri, ["accounts_receivable", "revenue"]

        # FSQ04: Revenue Quality (CFO / Revenue)
        if var_id == "FSQ04" and cfo is not None and rev and rev > 0:
            return (cfo / rev) * 100, ["cfo", "revenue"]

        # CFI01: CFO / PAT
        if var_id == "CFI01" and cfo is not None and pat and pat != 0:
            return cfo / pat, ["cfo", "pat"]

        # AQ01: Total Accruals / Assets
        if var_id == "AQ01" and pat is not None and cfo is not None and total_assets and total_assets > 0:
            return (pat - cfo) / total_assets, ["pat", "cfo", "total_assets"]

        # WCH01: DSO (Days Sales Outstanding)
        if var_id == "WCH01" and ar and rev and rev > 0:
            return (ar / rev) * 365.0, ["accounts_receivable", "revenue"]

        # WCH04: DIO (Days Inventory Outstanding)
        if var_id == "WCH04" and inv and cogs and cogs > 0:
            return (inv / cogs) * 365.0, ["inventory", "cogs"]

        # WCH07: DPO (Days Payables Outstanding)
        if var_id == "WCH07" and ap and cogs and cogs > 0:
            return (ap / cogs) * 365.0, ["accounts_payable", "cogs"]

        # WCH10: Cash Conversion Cycle (CCC)
        if var_id == "WCH10" and ar and inv and ap and rev and cogs and rev > 0 and cogs > 0:
            dso = (ar / rev) * 365.0
            dio = (inv / cogs) * 365.0
            dpo = (ap / cogs) * 365.0
            return dso + dio - dpo, ["accounts_receivable", "inventory", "accounts_payable"]

        # BSI02: Asset Quality Index (AQI)
        if var_id == "BSI02" and total_assets and prior_assets and total_assets > 0 and prior_assets > 0:
            # Simplified non-current asset ratio index
            return (total_assets / prior_assets), ["total_assets", "prior_total_assets"]

        return None, []
