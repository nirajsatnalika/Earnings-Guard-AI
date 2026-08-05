"""Pydantic v2 schemas for pillar score results, execution metadata, and variable traceability."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VariableTraceabilitySchema(BaseModel):
    """Schema for individual sub-variable traceability within a pillar."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Sub-variable name (e.g. CFO/PAT).")
    value: Optional[float] = Field(default=None, description="Computed raw variable value.")
    weight: float = Field(description="Weight assigned to this sub-variable.")
    contribution: float = Field(description="Calculated score contribution.")
    status: str = Field(default="computed", description="Status: computed | missing_input | division_by_zero")


class PillarExecutionMetadataSchema(BaseModel):
    """Execution metadata tracked per pillar run."""

    model_config = ConfigDict(extra="forbid")

    execution_time_ms: float = Field(ge=0, description="Pillar calculation time in milliseconds.")
    variables_used: List[str] = Field(default_factory=list, description="Variables consumed by this pillar.")
    variables_missing: List[str] = Field(default_factory=list, description="Variables required but missing.")
    variables_ignored: List[str] = Field(default_factory=list, description="Variables ignored during calculation.")
    warnings: List[str] = Field(default_factory=list, description="Warnings or caveats raised during execution.")


class PillarScoreSchema(BaseModel):
    """Pillar evaluation result schema matching target framework requirements."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Name of the financial pillar.")
    canonical_key: str = Field(description="Canonical key identifier.")
    score: float = Field(ge=0, le=100, description="Pillar score (0-100).")
    weight: float = Field(ge=0, le=1, description="Weight assigned to this pillar.")
    status: str = Field(default="computed", description="Status: computed | missing_input | ineligible | error")
    variables_used: List[str] = Field(default_factory=list, description="List of variable names used by this pillar.")
    strengths: List[str] = Field(default_factory=list, description="Positive forensic indicators.")
    weaknesses: List[str] = Field(default_factory=list, description="Weak or elevated risk indicators.")
    red_flags: List[str] = Field(default_factory=list, description="Critical forensic accounting red flags.")
    execution_metadata: PillarExecutionMetadataSchema = Field(description="Execution performance & metadata.")
    variable_traceability: List[VariableTraceabilitySchema] = Field(
        default_factory=list, description="Granular sub-variable score contributions."
    )
