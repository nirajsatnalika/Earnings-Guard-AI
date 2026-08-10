"""Pydantic v2 schemas for EFS™ AI Forensic Narrative outputs."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class KeyFindingNarrative(BaseModel):
    """Structured breakdown for a key forensic finding."""

    rule_id: Optional[str] = Field(None, description="Triggered rule ID if applicable (e.g. FR-001).")
    title: str = Field(..., description="Short descriptive title of what was observed.")
    what_observed: str = Field(..., description="Factual description of observed financial statement behavior.")
    why_it_matters: str = Field(..., description="Forensic context on accounting significance.")
    supporting_evidence: str = Field(..., description="Specific values, variable IDs, or rules supporting this finding.")
    legitimate_explanations: List[str] = Field(
        default_factory=list,
        description="Legitimate business or accounting alternative explanations.",
    )
    investigation_next_steps: str = Field(..., description="Recommended forensic audit/investigation step.")
    evidence_refs: List[str] = Field(
        default_factory=list,
        description="Underlying variable or rule IDs (e.g. ['FSQ02', 'FR-012']).",
    )


class PillarNarrative(BaseModel):
    """Structured narrative for one of the seven EFS pillars."""

    pillar_id: str = Field(..., description="Pillar ID (e.g. P1, P2).")
    pillar_name: str = Field(..., description="Pillar name.")
    summary: str = Field(..., description="Synthesis of pillar evidence.")
    positive_signals: List[str] = Field(default_factory=list, description="Favorable financial quality indicators.")
    adverse_signals: List[str] = Field(default_factory=list, description="Adverse forensic quality indicators.")
    missing_evidence: List[str] = Field(default_factory=list, description="Unavailable variables or disclosures.")
    investigation_areas: List[str] = Field(default_factory=list, description="Targeted follow-up areas.")


class ModelInterpretation(BaseModel):
    """Interpretation of an established academic forensic/credit model."""

    model_id: str = Field(..., description="Model ID (e.g. MODEL01).")
    model_name: str = Field(..., description="Model name (e.g. Beneish M-Score).")
    meaning: str = Field(..., description="What the model result indicates in plain English.")
    role_in_efs: str = Field(..., description="EFS framework role (Supporting Evidence vs Cross-Validation).")
    limitations: str = Field(..., description="Model-specific limitations or missing data constraints.")


class CrossSignalAnalysisItem(BaseModel):
    """Analysis of multiple converging signals across distinct financial dimensions."""

    theme: str = Field(..., description="Theme of signal convergence (e.g. Revenue Quality & Cash Conversion).")
    converging_signals: List[str] = Field(..., description="Descriptions of converging indicators.")
    explanation: str = Field(..., description="Combined forensic significance of converging signals.")
    cited_variables: List[str] = Field(default_factory=list, description="Variable IDs involved.")
    cited_rules: List[str] = Field(default_factory=list, description="Rule IDs involved.")


class EFSNarrativeResponse(BaseModel):
    """Overall structured AI Narrative response matching framework contract."""

    model_config = ConfigDict(extra="ignore")

    narrative_version: str = Field(default="1.0", description="Schema/narrative template version.")
    analysis_id: str = Field(..., description="Analysis ID from backend assessment.")
    assessment_id: str = Field(..., description="Deterministic assessment execution ID.")
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO timestamp of narrative generation.",
    )
    executive_summary: str = Field(..., description="Concise forensic executive summary.")
    overall_interpretation: str = Field(
        ...,
        description="Explanation of calibration-pending score and evidence-based interpretation.",
    )
    key_findings: List[KeyFindingNarrative] = Field(default_factory=list, description="Prioritized material findings.")
    pillar_narratives: List[PillarNarrative] = Field(
        default_factory=list, description="Narratives for all seven EFS pillars."
    )
    model_interpretations: List[ModelInterpretation] = Field(
        default_factory=list, description="Interpretations for 5 established models."
    )
    cross_signal_analysis: List[CrossSignalAnalysisItem] = Field(
        default_factory=list, description="Multi-signal convergence analysis."
    )
    investigation_priorities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Prioritized forensic investigation steps."
    )
    management_questions_context: List[Dict[str, Any]] = Field(
        default_factory=list, description="Context for management questions."
    )
    data_limitations: List[str] = Field(default_factory=list, description="Explicit evidence gaps.")
    methodology_note: str = Field(
        default="EFS™ is a deterministic financial forensics framework. The AI layer provides narrative interpretation of backend evidence without modifying scores, weights, or rule triggers.",
        description="Methodology and scope disclaimer.",
    )
    disclaimer: str = Field(
        default="AI-GENERATED FORENSIC INTERPRETATION. The deterministic EFS™ engine remains the forensic assessment authority. The AI explains the evidence; it does not calculate, score, classify, or modify findings.",
        description="Legal and professional disclaimer.",
    )
    provider_info: Dict[str, Any] = Field(
        default_factory=lambda: {"provider": "deterministic-fallback", "model": "rule-based-synthesizer", "fallback_used": True},
        description="Metadata on AI provider execution or fallback status.",
    )
