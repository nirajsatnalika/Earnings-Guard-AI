"""EFS™ Engine Framework Module."""

from app.calculations.efs.confidence_engine import ConfidenceEngine
from app.calculations.efs.engine import EFSEngine
from app.calculations.efs.exceptions import (
    EFSCalculationError,
    EFSConfigurationError,
    EFSDataValidationError,
    EFSEligibilityError,
    EFSEngineError,
    EFSPillarNotFoundError,
)
from app.calculations.efs.explainability_engine import ExplainabilityEngine
from app.calculations.efs.methodology_loader import MethodologyLoader
from app.calculations.efs.models import (
    AuditTrail,
    EFSExecutionResult,
    EFSInputVariables,
    ExplainabilityResult,
    MethodologyConfig,
    PillarExecutionMetadata,
    PillarResult,
    VariableTraceability,
)
from app.calculations.efs.pillars import PillarEngineRegistry
from app.calculations.efs.router import router
from app.calculations.efs.rules import (
    ForensicRule,
    ForensicRuleEngine,
    RuleCategory,
    RuleExecutor,
    RuleLoader,
    RuleSeverity,
    TriggeredRuleFinding,
)
from app.calculations.efs.schemas import (
    AuditTrailSchema,
    EFSRequest,
    EFSResponse,
    ExplainabilitySchema,
    PillarExecutionMetadataSchema,
    PillarScoreSchema,
    VariableTraceabilitySchema,
)
from app.calculations.efs.scoring_engine import ScoringEngine
from app.calculations.efs.validation_layer import ValidationLayer

__all__ = [
    "EFSEngine",
    "ForensicRuleEngine",
    "RuleLoader",
    "RuleExecutor",
    "ForensicRule",
    "RuleSeverity",
    "RuleCategory",
    "TriggeredRuleFinding",
    "MethodologyLoader",
    "ValidationLayer",
    "ScoringEngine",
    "ConfidenceEngine",
    "ExplainabilityEngine",
    "PillarEngineRegistry",
    "router",
    "EFSRequest",
    "EFSResponse",
    "AuditTrailSchema",
    "ExplainabilitySchema",
    "PillarScoreSchema",
    "VariableTraceabilitySchema",
    "PillarExecutionMetadataSchema",
    "EFSEngineError",
    "EFSConfigurationError",
    "EFSDataValidationError",
    "EFSEligibilityError",
    "EFSPillarNotFoundError",
    "EFSCalculationError",
    "EFSInputVariables",
    "MethodologyConfig",
    "PillarResult",
    "VariableTraceability",
    "PillarExecutionMetadata",
    "AuditTrail",
    "ExplainabilityResult",
    "EFSExecutionResult",
]
