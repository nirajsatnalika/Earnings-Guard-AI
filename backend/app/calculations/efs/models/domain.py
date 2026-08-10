"""Domain models and dataclasses for the EFS™ Assessment Framework.

Defines internal domain entities for input variables, pillar results, variable traceability,
established models, forensic rule findings, regulatory audit trails, and explainability outputs.
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
class EFSVariableResult:
    """Domain model representing an individual evaluated EFS variable."""

    variable_id: str
    variable_name: str
    pillar: str
    raw_value: Optional[float]
    unit: str
    score: Optional[int] = None
    scoring_band: Optional[str] = None
    data_status: str = "AVAILABLE"  # AVAILABLE, MISSING, NOT_APPLICABLE, INSUFFICIENT_EVIDENCE
    source_fields: List[str] = field(default_factory=list)
    calculation_status: str = "COMPLETED"


@dataclass
class EstablishedModelResult:
    """Domain representation of an established financial model result."""

    model_id: str
    model_name: str
    score: Optional[float]
    status: str  # COMPLETED, INSUFFICIENT_DATA, INELIGIBLE
    interpretation: str
    role: str  # Supporting Evidence, Cross-Validation
    details: Dict[str, Any] = field(default_factory=dict)


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

    pillar_id: str
    pillar_name: str
    pillar_score: Optional[float]
    variables_evaluated: int
    variables_available: int
    variables_missing: List[str] = field(default_factory=list)
    key_positive_drivers: List[str] = field(default_factory=list)
    key_negative_drivers: List[str] = field(default_factory=list)
    data_quality: str = "HIGH"  # HIGH, MEDIUM, LOW, INSUFFICIENT
    status: str = "COMPLETED"  # COMPLETED, INELIGIBLE, CALIBRATION_PENDING
    variables: List[EFSVariableResult] = field(default_factory=list)
    execution_metadata: PillarExecutionMetadata = field(
        default_factory=lambda: PillarExecutionMetadata(execution_time_ms=0.0)
    )


@dataclass
class ForensicRuleFinding:
    """Domain model representing an evaluated forensic rule finding."""

    rule_id: str
    rule_name: str
    pillar: str
    triggered: bool
    severity: str  # Critical, High, Medium, Low, Context
    trigger_condition: str
    evidence: str
    forensic_finding: str
    why_it_matters: str
    recommended_investigation: str
    question_for_management: str
    evidence_state: str = "Triggered"  # Triggered, Not Triggered, Not Evaluated, Not Applicable, Insufficient Evidence


@dataclass
class MethodologyConfig:
    """Container for dynamically loaded methodology parameters."""

    efs_version: str
    pillar_weights: Dict[str, Any]
    sub_variable_weights: Any
    risk_bands: Dict[str, Dict[str, Any]]
    confidence_factors: Dict[str, float]
    registered_variables: Dict[str, List[str]]
    eligibility_rules: Dict[str, Any]
    evaluation_rules: List[Dict[str, Any]]
    raw_config: Dict[str, Any] = field(default_factory=dict)


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

    assessment_id: str
    analysis_id: str
    efs_version: str
    scoring_version: str
    rulebook_version: str
    engine_version: str
    timestamp: str
    variables_evaluated: int
    variables_available: int
    rules_evaluated: int
    rules_triggered: int
    calculation_time_ms: float


@dataclass
class ConfidenceResult:
    """Domain representation of multi-factor confidence computation."""

    confidence_score: float
    confidence_level: str  # High, Medium, Low
    confidence_factors: Dict[str, float]
    limitations: List[str]


@dataclass
class EFSOverallResult:
    """Domain representation of overall score aggregation."""

    score: Optional[float]
    score_status: str  # CALIBRATION_PENDING, COMPUTED
    risk_level: Optional[str]
    confidence: float


@dataclass
class ExplainabilityResult:
    """Domain model representing synthesized forensic explainability."""

    observations: List[str] = field(default_factory=list)
    positive_drivers: List[str] = field(default_factory=list)
    negative_drivers: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    questions_for_management: List[str] = field(default_factory=list)


@dataclass
class EFSExecutionResult:
    """Complete domain result produced by the EFS Engine execution pipeline."""

    assessment_id: str
    analysis_id: str
    efs_version: str
    status: str
    overall: EFSOverallResult
    pillars: List[PillarResult]
    established_models: Dict[str, Any]
    forensic_findings: List[ForensicRuleFinding]
    red_flags: List[str]
    management_questions: List[str]
    limitations: List[str]
    audit_trail: AuditTrail
    explainability: ExplainabilityResult
