"""FastAPI router for EFS™ Framework endpoints."""

import logging
from fastapi import APIRouter, HTTPException, status

from app.calculations.efs.engine import EFSEngine
from app.calculations.efs.exceptions.base import EFSEngineError
from app.calculations.efs.schemas import (
    AuditTrailSchema,
    EFSRequest,
    EFSResponse,
    ExplainabilitySchema,
    PillarExecutionMetadataSchema,
    PillarScoreSchema,
    VariableTraceabilitySchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/efs", tags=["efs"])

# Shared engine instance
efs_engine = EFSEngine()


@router.post(
    "/{analysis_id}",
    response_model=EFSResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Earnings Financial Safety (EFS™) Forensic Score",
    description="Methodology-driven engine evaluating financial statement quality across 7 pillars.",
)
async def calculate_efs(
    analysis_id: str,
    payload: EFSRequest = EFSRequest(),
) -> EFSResponse:
    """POST endpoint calculating EFS forensic assessment for a given analysis_id."""
    logger.info("Received POST /api/v1/efs/%s", analysis_id)
    try:
        input_data = payload.model_dump()
        result = efs_engine.run(analysis_id=analysis_id, input_payload=input_data)

        # Convert domain models to response schemas
        pillar_schemas = []
        for p in result.pillar_scores:
            traceability_schemas = [
                VariableTraceabilitySchema(
                    name=vt.name,
                    value=vt.value,
                    weight=vt.weight,
                    contribution=vt.contribution,
                    status=vt.status,
                )
                for vt in p.variable_traceability
            ]

            meta_schema = PillarExecutionMetadataSchema(
                execution_time_ms=p.execution_metadata.execution_time_ms,
                variables_used=p.execution_metadata.variables_used,
                variables_missing=p.execution_metadata.variables_missing,
                variables_ignored=p.execution_metadata.variables_ignored,
                warnings=p.execution_metadata.warnings,
            )

            pillar_schemas.append(
                PillarScoreSchema(
                    name=p.name,
                    canonical_key=p.canonical_key,
                    score=p.score,
                    weight=p.weight,
                    status=p.status,
                    variables_used=p.variables_used,
                    strengths=p.strengths,
                    weaknesses=p.weaknesses,
                    red_flags=p.red_flags,
                    execution_metadata=meta_schema,
                    variable_traceability=traceability_schemas,
                )
            )

        audit_schema = AuditTrailSchema(
            execution_id=result.audit_trail.execution_id,
            timestamp=result.audit_trail.timestamp,
            efs_version=result.audit_trail.efs_version,
            engine_version=result.audit_trail.engine_version,
            inputs_used=result.audit_trail.inputs_used,
            variables_used_count=result.audit_trail.variables_used_count,
            calculation_time_ms=result.audit_trail.calculation_time_ms,
            rules_evaluated_count=result.audit_trail.rules_evaluated_count,
            rules_triggered_count=result.audit_trail.rules_triggered_count,
        )

        explain_schema = ExplainabilitySchema(
            observations=result.explainability.observations,
            positive_drivers=result.explainability.positive_drivers,
            negative_drivers=result.explainability.negative_drivers,
            red_flags=result.explainability.red_flags,
            recommendations=result.explainability.recommendations,
            questions_for_management=result.explainability.questions_for_management,
        )

        return EFSResponse(
            analysis_id=result.analysis_id,
            efs_version=result.efs_version,
            overall_score=result.overall_score,
            confidence=result.confidence,
            manipulation_risk=result.manipulation_risk,
            audit_trail=audit_schema,
            pillar_scores=pillar_schemas,
            explainability=explain_schema,
        )
    except EFSEngineError as err:
        logger.warning("EFS calculation domain error for analysis_id=%s: %s", analysis_id, err.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": err.message, "details": err.details},
        )
    except Exception as exc:
        logger.exception("Unexpected error during EFS calculation for analysis_id=%s: %s", analysis_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during EFS calculation: {str(exc)}",
        )
