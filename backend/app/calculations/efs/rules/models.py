"""Domain models and enums for the Financial Forensics Rule Engine."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RuleSeverity(str, Enum):
    """Supported rule severity levels."""

    INFO = "Info"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RuleCategory(str, Enum):
    """Supported forensic rule categories."""

    REVENUE_RECOGNITION = "Revenue Recognition"
    CASH_FLOW = "Cash Flow"
    ACCRUALS = "Accruals"
    WORKING_CAPITAL = "Working Capital"
    BALANCE_SHEET = "Balance Sheet"
    GROWTH_QUALITY = "Growth Quality"
    GOVERNANCE = "Governance"


@dataclass
class RuleCondition:
    """Structure defining evaluation condition logic for a forensic rule."""

    operator: str
    left_variable: str
    right_variable: Optional[str] = None
    threshold: Optional[float] = None
    value: Optional[Any] = None


@dataclass
class ForensicRule:
    """Domain representation of a dynamically loaded forensic rule."""

    rule_id: str
    category: str
    severity: str
    condition: RuleCondition
    message: str
    recommendation: str
    question_for_management: str
    priority: int = 10
    group: str = "general"
    enabled: bool = True
    version: str = "1.0"
    variables_used: List[str] = field(default_factory=list)


@dataclass
class TriggeredRuleFinding:
    """Forensic observation finding generated when a rule condition is met."""

    rule_id: str
    category: str
    severity: str
    message: str
    recommendation: str
    question_for_management: str
    variables_used: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleExecutionSummary:
    """Execution statistics for a rule evaluation run."""

    rules_evaluated_count: int
    rules_triggered_count: int
    execution_time_ms: float
