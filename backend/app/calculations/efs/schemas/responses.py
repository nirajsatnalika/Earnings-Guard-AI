"""Pydantic v2 schemas for EFS™ Engine API responses."""

from typing import List
from pydantic import BaseModel, ConfigDict, Field

from app.calculations.efs.schemas.audit import AuditTrailSchema
from app.calculations.efs.schemas.pillars import PillarScoreSchema


class ExplainabilitySchema(BaseModel):
    """Forensic explainability schema returning 6 qualitative categories."""

    model_config = ConfigDict(extra="forbid")

    observations: List[str] = Field(description="Forensic observation highlights.")
    positive_drivers: List[str] = Field(description="Positive earnings quality drivers.")
    negative_drivers: List[str] = Field(description="Negative risk drivers.")
    red_flags: List[str] = Field(description="Critical earnings manipulation red flags.")
    recommendations: List[str] = Field(description="Forensic audit & review recommendations.")
    questions_for_management: List[str] = Field(description="Targeted questions for corporate management.")


class EFSResponse(BaseModel):
    """Overall EFS Engine response matching exact framework contract."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str = Field(description="Unique identifier for the financial analysis.")
    efs_version: str = Field(default="1.0", description="EFS methodology version used.")
    overall_score: float = Field(description="Overall EFS Score (0-100).")
    confidence: float = Field(description="Multi-factor data confidence score (0-100).")
    manipulation_risk: str = Field(description="Risk classification: Low | Moderate | High | Critical.")
    audit_trail: AuditTrailSchema = Field(description="Regulatory audit trail metadata.")
    pillar_scores: List[PillarScoreSchema] = Field(description="Scores breakdown across all seven pillars.")
    explainability: ExplainabilitySchema = Field(description="Structured forensic explainability breakdown.")
