"""Feature Engineering service — orchestrates derived metric calculation.

Reads parsed DataFrames and canonical-to-label mappings from the Parser and
Mapping engines, builds a ValueStore, executes every registered feature
function, and returns a structured response with a flat dataset map ready
for downstream models (Beneish, ratios, ML pipelines).
"""

from __future__ import annotations

from collections import defaultdict

from app.calculations.features import ALL_FEATURES
from app.calculations.ratios.calculation_utils import ValueStore
from app.core.exceptions import AnalysisNotFoundError
from app.core.logging import get_logger
from app.schemas.features import DerivedMetric, FeatureGroupSummary, FeatureResponse
from app.services.mapping_service import MappingService
from app.services.parser_service import ParserService

logger = get_logger(__name__)

# In-memory store: analysis_id -> FeatureResponse
_feature_store: dict[str, FeatureResponse] = {}


class FeatureService:
    """Computes all derived features for a validated analysis."""

    @staticmethod
    def engineer(analysis_id: str) -> FeatureResponse:
        frames = ParserService.get_frames(analysis_id)
        mappings = MappingService.get_mappings(analysis_id)

        if frames is None or mappings is None:
            logger.warning("Features requested for unprocessed analysis %s", analysis_id)
            raise AnalysisNotFoundError(analysis_id)

        # Build canonical-to-label mapping from the mapping store.
        canonical_to_labels: dict[str, list[str]] = {}
        for statement_mappings in mappings.values():
            for sheet_mappings in statement_mappings.values():
                for raw_label, mapped in sheet_mappings.items():
                    canonical_to_labels.setdefault(mapped.mapped, []).append(raw_label)

        value_store = ValueStore(frames, canonical_to_labels)

        features: list[DerivedMetric] = []
        dataset: dict[str, float | None] = {}
        summary: dict[str, int] = {"computed": 0, "missing_input": 0, "division_by_zero": 0}
        group_counts: dict[str, dict[str, int]] = defaultdict(
            lambda: {"total": 0, "computed": 0, "missing_input": 0, "division_by_zero": 0}
        )

        for feature_fn in ALL_FEATURES:
            fn_name = getattr(feature_fn, "__name__", str(feature_fn))
            try:
                result = feature_fn(value_store)
            except Exception:
                logger.exception(
                    "Analysis %s: feature function '%s' raised an unexpected error",
                    analysis_id,
                    fn_name,
                )
                result = DerivedMetric(
                    name=fn_name,
                    category="unknown",
                    value=None,
                    status="missing_input",
                    formula="",
                    inputs={},
                    interpretation="Unexpected error during calculation.",
                )

            features.append(result)
            dataset[result.name] = result.value
            summary[result.status] = summary.get(result.status, 0) + 1
            group_counts[result.category]["total"] += 1
            group_counts[result.category][result.status] += 1
            logger.info(
                "Analysis %s: feature '%s' (%s) = %s [%s]",
                analysis_id,
                result.name,
                result.category,
                f"{result.value:.4f}" if result.value is not None else "N/A",
                result.status,
            )

        groups = [
            FeatureGroupSummary(
                category=cat,
                total=counts["total"],
                computed=counts["computed"],
                missing_input=counts["missing_input"],
                division_by_zero=counts["division_by_zero"],
            )
            for cat, counts in sorted(group_counts.items())
        ]

        overall_status = "computed" if summary["missing_input"] == 0 and summary["division_by_zero"] == 0 else "partial"

        response = FeatureResponse(
            analysis_id=analysis_id,
            status=overall_status,
            total_features=len(features),
            features=features,
            dataset=dataset,
            summary=summary,
            groups=groups,
        )

        _feature_store[analysis_id] = response
        logger.info(
            "Analysis %s: feature engineering complete — %d total, %d computed, %d missing, %d div-zero",
            analysis_id,
            len(features),
            summary["computed"],
            summary["missing_input"],
            summary["division_by_zero"],
        )
        return response

    @staticmethod
    def get_result(analysis_id: str) -> FeatureResponse | None:
        """Access the in-memory feature results for an analysis, if present."""
        return _feature_store.get(analysis_id)
