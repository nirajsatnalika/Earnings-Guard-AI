"""Pydantic v2 schemas for EFS™ Engine API responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EFSVariableSchema(BaseModel):
    """Schema for individual evaluated EFS variable."""

    variable_id: str
    variable_name: str
    pillar: str
    raw_value: Optional[float] = None
    unit: str
    score: Optional[int] = None
    scoring_band: Optional[str] = None
    data_status: str
    source_fields: List[str] = Field(default_factory=list)
    calculation_status: str


class PillarSchema(BaseModel):
    """Schema for individual pillar evaluation result."""

    pillar_id: str
    pillar_name: str
    pillar_score: Optional[float] = None
    variables_evaluated: int
    variables_available: int
    variables_missing: List[str] = Field(default_factory=list)
    key_positive_drivers: List[str] = Field(default_factory=list)
    key_negative_drivers: List[str] = Field(default_factory=list)
    data_quality: str
    status: str
    variables: List[EFSVariableSchema] = Field(default_factory=list)


class OverallSchema(BaseModel):
    """Schema for overall assessment scores and calibration status."""

    score: Optional[float] = None
    score_status: str
    risk_level: Optional[str] = None
    confidence: float


class EstablishedModelsSchema(BaseModel):
    """Schema for established models outputs."""

    beneish_m_score: Dict[str, Any] = Field(default_factory=dict)
    sloan_accrual: Dict[str, Any] = Field(default_factory=dict)
    altman_z_score: Dict[str, Any] = Field(default_factory=dict)
    piotroski_f_score: Dict[str, Any] = Field(default_factory=dict)
    ohlson_o_score: Dict[str, Any] = Field(default_factory=dict)


class ForensicFindingSchema(BaseModel):
    """Schema for evaluated forensic rule finding."""

    rule_id: str
    rule_name: str
    pillar: str
    triggered: bool
    severity: str
    trigger_condition: str
    evidence: str
    forensic_finding: str
    why_it_matters: str
    recommended_investigation: str
    question_for_management: str
    evidence_state: str = "Triggered"


class AuditTrailSchema(BaseModel):
    """Schema for regulatory audit trail."""

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


class EFSResponse(BaseModel):
    """Overall EFS Engine response matching exact framework contract."""

    model_config = ConfigDict(extra="ignore")

    assessment_id: str = Field(description="Unique assessment execution identifier.")
    analysis_id: str = Field(description="Unique identifier for the financial analysis.")
    efs_version: str = Field(default="1.0", description="EFS methodology version used.")
    status: str = Field(default="COMPLETED", description="Assessment processing status.")
    overall: OverallSchema = Field(description="Overall EFS score, status, risk level, and confidence.")
    pillars: List[PillarSchema] = Field(description="Results across all seven methodology pillars.")
    established_models: EstablishedModelsSchema = Field(description="Results of 5 established financial models.")
    forensic_findings: List[ForensicFindingSchema] = Field(description="Evaluated forensic rules and findings.")
    red_flags: List[str] = Field(description="High-level forensic red flag summary.")
    management_questions: List[str] = Field(description="Recommended management inquiry questions.")
    limitations: List[str] = Field(description="Data quality or availability limitations.")
    audit_trail: AuditTrailSchema = Field(description="Regulatory audit trail metadata.")
