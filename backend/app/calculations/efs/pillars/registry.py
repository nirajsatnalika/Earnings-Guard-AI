"""Pillar Registry managing all 7 EFS pillar engine implementations."""

from typing import Dict, List
from app.calculations.efs.exceptions.base import EFSPillarNotFoundError
from app.calculations.efs.models.domain import (
    EFSInputVariables,
    MethodologyConfig,
    PillarResult,
)
from app.calculations.efs.pillars.accrual_quality import AccrualQualityPillar
from app.calculations.efs.pillars.balance_sheet_integrity import (
    BalanceSheetIntegrityPillar,
)
from app.calculations.efs.pillars.base import BasePillarEngine
from app.calculations.efs.pillars.cash_flow_integrity import CashFlowIntegrityPillar
from app.calculations.efs.pillars.financial_statement_quality import (
    FinancialStatementQualityPillar,
)
from app.calculations.efs.pillars.governance_disclosure import (
    GovernanceDisclosurePillar,
)
from app.calculations.efs.pillars.growth_sustainability import (
    GrowthSustainabilityPillar,
)
from app.calculations.efs.pillars.working_capital_health import (
    WorkingCapitalHealthPillar,
)


class PillarEngineRegistry:
    """Registry maintaining active pillar engines."""

    def __init__(self) -> None:
        self._pillars: Dict[str, BasePillarEngine] = {
            "financial_statement_quality": FinancialStatementQualityPillar(),
            "cash_flow_integrity": CashFlowIntegrityPillar(),
            "accrual_quality": AccrualQualityPillar(),
            "working_capital_health": WorkingCapitalHealthPillar(),
            "balance_sheet_integrity": BalanceSheetIntegrityPillar(),
            "growth_sustainability": GrowthSustainabilityPillar(),
            "governance_disclosure": GovernanceDisclosurePillar(),
        }

    def get_pillar(self, canonical_key: str) -> BasePillarEngine:
        """Retrieves a specific pillar engine."""
        if canonical_key not in self._pillars:
            raise EFSPillarNotFoundError(f"Pillar engine '{canonical_key}' is not registered.")
        return self._pillars[canonical_key]

    def calculate_all(
        self, variables: EFSInputVariables, methodology: MethodologyConfig
    ) -> List[PillarResult]:
        """Calculates results across all 7 registered pillars using loaded methodology weights."""
        results: List[PillarResult] = []
        weights_map = methodology.pillar_weights

        for canonical_key, engine in self._pillars.items():
            weight = weights_map.get(canonical_key, 0.0)
            result = engine.calculate(
                variables=variables, weight=weight, methodology=methodology
            )
            results.append(result)

        return results
