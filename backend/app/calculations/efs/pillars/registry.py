"""Pillar Registry managing all 7 frozen EFS pillar evaluation engines."""

import logging
import time
from typing import Dict, List, Optional

from app.calculations.efs.models.domain import (
    EFSInputVariables,
    EFSVariableResult,
    MethodologyConfig,
    PillarExecutionMetadata,
    PillarResult,
)

logger = logging.getLogger(__name__)

# Frozen 7 Pillars specification
FROZEN_PILLARS = [
    ("P1", "Financial Statement Quality", "Financial Statement Quality"),
    ("P2", "Cash Flow Integrity", "Cash Flow Integrity"),
    ("P3", "Accrual & Accounting Quality", "Accrual & Accounting Quality"),
    ("P4", "Working Capital Forensics", "Working Capital Forensics"),
    ("P5", "Balance Sheet Integrity", "Balance Sheet Integrity"),
    ("P6", "Earnings Sustainability & Growth Quality", "Earnings Sustainability & Growth Quality"),
    ("P7", "Governance, Disclosure & External Evidence", "Governance, Disclosure & External Evidence"),
]


class PillarEngineRegistry:
    """Registry maintaining active pillar engines across the 7 frozen methodology pillars."""

    def calculate_all(
        self,
        computed_variables: Dict[str, EFSVariableResult],
        variables_input: EFSInputVariables,
        methodology: MethodologyConfig,
    ) -> List[PillarResult]:
        """Groups computed variables into the 7 methodology pillars."""
        pillar_results: List[PillarResult] = []

        for p_id, p_name, p_key in FROZEN_PILLARS:
            start_t = time.perf_counter()
            
            # Filter variables belonging to this pillar
            pillar_vars = [
                v for v in computed_variables.values()
                if v.pillar.strip().lower() == p_name.strip().lower()
                or (v.variable_id.startswith("FSQ") and p_id == "P1")
                or (v.variable_id.startswith("CFI") and p_id == "P2")
                or (v.variable_id.startswith("AQ") and p_id == "P3")
                or (v.variable_id.startswith("WCH") and p_id == "P4")
                or (v.variable_id.startswith("BSI") and p_id == "P5")
                or (v.variable_id.startswith("GS") and p_id == "P6")
                or (v.variable_id.startswith("GD") and p_id == "P7")
            ]

            eval_count = len(pillar_vars)
            available_vars = [v for v in pillar_vars if v.data_status == "AVAILABLE"]
            missing_ids = [v.variable_id for v in pillar_vars if v.data_status != "AVAILABLE"]

            avail_count = len(available_vars)
            
            # Compute data quality label
            avail_pct = (avail_count / max(eval_count, 1)) * 100
            if avail_pct >= 80.0:
                dq_label = "HIGH"
            elif avail_pct >= 50.0:
                dq_label = "MEDIUM"
            elif avail_pct > 0.0:
                dq_label = "LOW"
            else:
                dq_label = "INSUFFICIENT"

            # Identify key positive and negative drivers based on scores
            pos_drivers = [v.variable_name for v in available_vars if v.score is not None and v.score >= 75]
            neg_drivers = [v.variable_name for v in available_vars if v.score is not None and v.score <= 25]

            # Statement ineligibility check
            is_ineligible = False
            if p_id == "P2" and not variables_input.statement_flags.get("has_cash_flow_statement", True):
                is_ineligible = True

            status = "INELIGIBLE" if is_ineligible else "CALIBRATION_PENDING"

            exec_meta = PillarExecutionMetadata(
                execution_time_ms=round((time.perf_counter() - start_t) * 1000, 2),
                variables_used=[v.variable_id for v in available_vars],
                variables_missing=missing_ids,
            )

            p_result = PillarResult(
                pillar_id=p_id,
                pillar_name=p_name,
                pillar_score=None,  # Calibration pending per frozen methodology
                variables_evaluated=eval_count,
                variables_available=avail_count,
                variables_missing=missing_ids,
                key_positive_drivers=pos_drivers,
                key_negative_drivers=neg_drivers,
                data_quality=dq_label,
                status=status,
                variables=pillar_vars,
                execution_metadata=exec_meta,
            )
            pillar_results.append(p_result)

        return pillar_results
