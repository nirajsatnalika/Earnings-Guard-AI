"""Regulatory Audit Trail schema for the EFS™ Framework."""

from typing import List
from pydantic import BaseModel, ConfigDict, Field


class AuditTrailSchema(BaseModel):
    """Regulatory audit trail schema ensuring transparency and reproducibility."""

    model_config = ConfigDict(extra="forbid")

    execution_id: str = Field(description="Unique UUID string identifying this execution run.")
    timestamp: str = Field(description="ISO-8601 timestamp of execution.")
    efs_version: str = Field(description="Version of EFS methodology loaded.")
    engine_version: str = Field(description="Version of EFS engine framework software.")
    inputs_used: List[str] = Field(description="List of upstream input engines utilized.")
    variables_used_count: int = Field(ge=0, description="Total count of variables evaluated.")
    calculation_time_ms: float = Field(ge=0, description="Total pipeline execution time in milliseconds.")
    rules_evaluated_count: int = Field(default=0, ge=0, description="Total forensic rules evaluated.")
    rules_triggered_count: int = Field(default=0, ge=0, description="Total forensic rules triggered.")
