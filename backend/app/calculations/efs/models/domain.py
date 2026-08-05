"""Domain models and dataclasses for the EFS™ Assessment Framework.

Defines internal domain entities for input variables, pillar results, variable traceability,
regulatory audit trails, and 6-category explainability outputs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VariableTraceability:
    """Sub-variable level score contribution and status tracking."""

    name: str
    value: Optional[float]
    weight: float
    contribution: float
    status: str = "computed"


@dataclass
class PillarExecutionMetadata:
    """Execution metadata tracked per pillar run."""

    execution_time_ms: float
    variables_used: List[str] = field(default_factory=list)
    variables_missing: List[str] = field(default_factory=list)
    variables_ignored: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class PillarResult:
    """Domain representation of an individual pillar evaluation result."""

    name: str
    canonical_key: str
    score: float
    weight: float
    status: str = "computed"
    variables_used: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    execution_metadata: PillarExecutionMetadata = field(
        default_factory=lambda: PillarExecutionMetadata(execution_time_ms=0.0)
    )
    variable_traceability: List[VariableTraceability] = field(default_factory=list)


@dataclass
class MethodologyConfig:
    """Container for dynamically loaded methodology parameters."""

    efs_version: str
    pillar_weights: Dict[str, float]
    sub_variable_weights: Dict[str, Dict[str, float]]
    risk_bands: Dict[str, Dict[str, Any]]
    confidence_factors: Dict[str, float]
    registered_variables: Dict[str, List[str]]
    eligibility_rules: Dict[str, Any]
    evaluation_rules: List[Dict[str, Any]]


@dataclass
class EFSInputVariables:
    """Unified container for all upstream engine inputs consumed by EFS."""

    analysis_id: str
    validation_data: Optional[Dict[str, Any]] = None
    feature_data: Optional[Dict[str, Any]] = None
    ratio_data: Optional[Dict[str, Any]] = None
    beneish_data: Optional[Dict[str, Any]] = None
    statement_flags: Dict[str, bool] = field(
        default_factory=lambda: {
            "has_cash_flow_statement": True,
            "has_balance_sheet": True,
            "has_income_statement": True,
        }
    )
    raw_variables: Dict[str, Any] = field(default_factory=dict)
    # Confidence metrics
    validation_completeness: float = 100.0
    parser_confidence: float = 100.0
    mapping_confidence: float = 100.0
    missing_financial_statements_count: int = 0
    missing_variables_count: int = 0
    validation_errors_count: int = 0


@dataclass
class AuditTrail:
    """Regulatory audit trail entity."""

    execution_id: str
    timestamp: str
    efs_version: str
    engine_version: str
    inputs_used: List[str]
    variables_used_count: int
    calculation_time_ms: float
    rules_evaluated_count: int = 0
    rules_triggered_count: int = 0


@dataclass
class ExplainabilityResult:
    """Domain model representing synthesized 6-category forensic explainability."""

    observations: List[str] = field(default_factory=list)
    positive_drivers: List[str] = field(default_factory=list)
    negative_drivers: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    questions_for_management: List[str] = field(default_factory=list)


@dataclass
class EFSExecutionResult:
    """Complete domain result produced by the EFS Engine execution pipeline."""

    analysis_id: str
    efs_version: str
    overall_score: float
    confidence: float
    manipulation_risk: str
    audit_trail: AuditTrail
    pillar_scores: List[PillarResult]
    explainability: ExplainabilityResult
