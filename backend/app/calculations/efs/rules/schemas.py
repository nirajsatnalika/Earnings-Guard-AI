"""Pydantic v2 schemas for the Financial Forensics Rule Engine."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ForensicRuleSchema(BaseModel):
    """Schema representing a forensic rule configuration."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(description="Unique rule identifier (e.g. RULE_REV_REC_01).")
    category: str = Field(description="Forensic category.")
    severity: str = Field(description="Severity: Info | Low | Medium | High | Critical.")
    group: str = Field(default="general", description="Rule group identifier.")
    priority: int = Field(default=10, description="Rule execution priority (higher runs earlier).")
    enabled: bool = Field(default=True, description="Master enable switch for rule.")
    version: str = Field(default="1.0", description="Rule methodology version.")
    message: str = Field(description="Forensic observation message.")
    recommendation: str = Field(description="Actionable forensic recommendation.")
    question_for_management: str = Field(description="Targeted question for corporate management.")
    variables_used: List[str] = Field(default_factory=list, description="Variables evaluated by this rule.")


class TriggeredRuleFindingSchema(BaseModel):
    """Schema for a single triggered forensic finding output."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(description="Unique rule identifier.")
    category: str = Field(description="Forensic category.")
    severity: str = Field(description="Severity level.")
    message: str = Field(description="Forensic observation message.")
    recommendation: str = Field(description="Actionable forensic recommendation.")
    question_for_management: str = Field(description="Question for corporate management.")
    variables_used: List[str] = Field(default_factory=list, description="Variables consumed in evaluation.")


class RuleExecutionSummarySchema(BaseModel):
    """Schema for rule engine execution summary metrics."""

    model_config = ConfigDict(extra="forbid")

    rules_evaluated_count: int = Field(ge=0, description="Total rules evaluated.")
    rules_triggered_count: int = Field(ge=0, description="Total rules triggered.")
    execution_time_ms: float = Field(ge=0, description="Rule execution time in milliseconds.")
