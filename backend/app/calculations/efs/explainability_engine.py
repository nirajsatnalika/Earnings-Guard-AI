"""Rule-Based Explainability Engine for the EFS™ Assessment Framework.

Synthesizes forensic assessment results and Rule Engine findings into 6 structured qualitative categories:
- observations
- positive_drivers
- negative_drivers
- red_flags
- recommendations
- questions_for_management

Utilizes rule-based findings without AI prompts or hardcoded financial formulas.
"""

import logging
from typing import List, Optional
from app.calculations.efs.interfaces.base import IExplainabilityEngine
from app.calculations.efs.models.domain import (
    EFSInputVariables,
    ExplainabilityResult,
    PillarResult,
)
from app.calculations.efs.rules.models import TriggeredRuleFinding

logger = logging.getLogger(__name__)


class ExplainabilityEngine(IExplainabilityEngine):
    """Engine synthesizing forensic pillar findings and Rule Engine observations into 6 explainability categories."""

    def generate_explainability(
        self,
        pillar_results: List[PillarResult],
        variables: EFSInputVariables,
        rule_findings: Optional[List[TriggeredRuleFinding]] = None,
    ) -> ExplainabilityResult:
        logger.debug(
            "Generating 6-category explainability outputs for analysis_id=%s (rule_findings=%d)",
            variables.analysis_id,
            len(rule_findings) if rule_findings else 0,
        )

        observations: List[str] = [
            "Forensic accounting evaluation completed across seven primary earnings quality pillars."
        ]
        positive_drivers: List[str] = []
        negative_drivers: List[str] = []
        red_flags: List[str] = []
        recommendations: List[str] = []
        questions_for_management: List[str] = []

        # 1. Collect pillar-level findings
        for pillar in pillar_results:
            positive_drivers.extend(pillar.strengths)
            negative_drivers.extend(pillar.weaknesses)
            red_flags.extend(pillar.red_flags)

        # 2. Integrate Rule Engine findings if provided
        if rule_findings:
            for finding in rule_findings:
                obs_text = f"[{finding.category}] {finding.message}"
                observations.append(obs_text)

                if finding.severity in ("High", "Critical"):
                    red_flags.append(f"[{finding.severity}] {finding.message}")
                elif finding.severity in ("Medium", "Low"):
                    negative_drivers.append(f"[{finding.category}] {finding.message}")
                elif finding.severity == "Info":
                    positive_drivers.append(f"[{finding.category}] {finding.message}")

                if finding.recommendation:
                    recommendations.append(finding.recommendation)
                if finding.question_for_management:
                    questions_for_management.append(finding.question_for_management)

        # 3. Fallbacks if empty
        if not positive_drivers:
            positive_drivers.append(
                "Framework Baseline: Reported financial statements pass baseline structural checks."
            )
        if not negative_drivers:
            negative_drivers.append(
                "Framework Baseline: Monitor working capital conversion cycles and quarterly accrual variance."
            )
        if not red_flags:
            red_flags.append(
                "Framework Baseline: No critical earnings manipulation red flags triggered in current dataset."
            )
        if not recommendations:
            recommendations.append(
                "Framework Placeholder: Perform targeted audit sampling on accounts receivable aging schedules."
            )
        if not questions_for_management:
            questions_for_management.append(
                "Framework Placeholder: What primary drivers contributed to the variance between net income and operating cash flow?"
            )

        return ExplainabilityResult(
            observations=observations,
            positive_drivers=positive_drivers,
            negative_drivers=negative_drivers,
            red_flags=red_flags,
            recommendations=recommendations,
            questions_for_management=questions_for_management,
        )
