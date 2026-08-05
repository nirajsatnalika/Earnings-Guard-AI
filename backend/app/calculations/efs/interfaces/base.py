"""Interfaces and Abstract Base Classes for the EFS™ Engine Framework."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.calculations.efs.models.domain import (
    EFSExecutionResult,
    EFSInputVariables,
    ExplainabilityResult,
    MethodologyConfig,
    PillarResult,
)


class IPillarEngine(ABC):
    """Interface for individual EFS Pillar Engines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display name of the pillar."""
        pass

    @property
    @abstractmethod
    def canonical_key(self) -> str:
        """Canonical key used for methodology and dict lookups."""
        pass

    @abstractmethod
    def calculate(
        self, variables: EFSInputVariables, weight: float, methodology: MethodologyConfig
    ) -> PillarResult:
        """Calculates score and extracts pillar findings and variable traceability.

        Returns:
            PillarResult containing score, status, variable traceability, execution metadata.
        """
        pass


class IMethodologyLoader(ABC):
    """Interface for dynamic methodology configuration loaders."""

    @abstractmethod
    def load(self, version: str = "1.0") -> MethodologyConfig:
        """Loads and parses weights, thresholds, variables, and rules."""
        pass


class IScoringEngine(ABC):
    """Interface for overall score aggregation engine."""

    @abstractmethod
    def aggregate_score(
        self, pillar_results: List[PillarResult], methodology: MethodologyConfig
    ) -> float:
        """Aggregates individual pillar scores into an overall score based on methodology weights."""
        pass

    @abstractmethod
    def determine_manipulation_risk(
        self, overall_score: float, methodology: MethodologyConfig
    ) -> str:
        """Determines manipulation risk label based on overall score."""
        pass


class IExplainabilityEngine(ABC):
    """Interface for generating 6-category structured explainability."""

    @abstractmethod
    def generate_explainability(
        self, pillar_results: List[PillarResult], variables: EFSInputVariables
    ) -> ExplainabilityResult:
        """Generates observations, positive_drivers, negative_drivers, red_flags, recommendations, questions_for_management."""
        pass


class IConfidenceEngine(ABC):
    """Interface for evaluating multi-factor confidence score."""

    @abstractmethod
    def calculate_confidence(
        self, variables: EFSInputVariables, methodology: MethodologyConfig
    ) -> float:
        """Calculates confidence score taking missing variables, disclosures, validation errors into account."""
        pass


class IEFSEngine(ABC):
    """Interface for top-level EFS Engine orchestrator."""

    @abstractmethod
    def run(
        self, analysis_id: str, input_payload: Dict[str, Any]
    ) -> EFSExecutionResult:
        """Executes full EFS calculation pipeline for a given analysis_id."""
        pass
