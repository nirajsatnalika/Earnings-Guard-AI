"""FastAPI router for EFS™ Assessment Engine endpoints."""

import logging
from fastapi import APIRouter, HTTPException, status

from app.calculations.efs.engine import EFSEngine
from app.calculations.efs.exceptions.base import EFSEngineError
from app.calculations.efs.schemas.requests import EFSRequest
from app.calculations.efs.schemas.responses import (
    AuditTrailSchema,
    EFSResponse,
    EFSVariableSchema,
    EstablishedModelsSchema,
    ForensicFindingSchema,
    OverallSchema,
    PillarSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/efs", tags=["efs"])

# Shared engine instance
efs_engine = EFSEngine()


@router.post(
    "/{analysis_id}",
    response_model=EFSResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Earnings Financial Safety (EFS™) Forensic Assessment",
    description="Methodology-driven deterministic engine evaluating financial statement quality across 7 pillars.",
)
async def calculate_efs(
    analysis_id: str,
    payload: EFSRequest = EFSRequest(),
) -> EFSResponse:
    """POST endpoint executing EFS forensic assessment for a given analysis_id."""
    logger.info("Received POST /api/v1/efs/%s", analysis_id)
    try:
        input_data = payload.model_dump()
        result = efs_engine.run(analysis_id=analysis_id, input_payload=input_data)

        # 1. Overall Schema
        overall_schema = OverallSchema(
            score=result.overall.score,
            score_status=result.overall.score_status,
            risk_level=result.overall.risk_level,
            confidence=result.overall.confidence,
        )

        # 2. Pillars Schema
        pillar_schemas = []
        for p in result.pillars:
            var_schemas = [
                EFSVariableSchema(
                    variable_id=v.variable_id,
                    variable_name=v.variable_name,
                    pillar=v.pillar,
                    raw_value=v.raw_value,
                    unit=v.unit,
                    score=v.score,
                    scoring_band=v.scoring_band,
                    data_status=v.data_status,
                    source_fields=v.source_fields,
                    calculation_status=v.calculation_status,
                )
                for v in p.variables
            ]

            pillar_schemas.append(
                PillarSchema(
                    pillar_id=p.pillar_id,
                    pillar_name=p.pillar_name,
                    pillar_score=p.pillar_score,
                    variables_evaluated=p.variables_evaluated,
                    variables_available=p.variables_available,
                    variables_missing=p.variables_missing,
                    key_positive_drivers=p.key_positive_drivers,
                    key_negative_drivers=p.key_negative_drivers,
                    data_quality=p.data_quality,
                    status=p.status,
                    variables=var_schemas,
                )
            )

        # 3. Established Models Schema
        models_schema = EstablishedModelsSchema(
            beneish_m_score=result.established_models.get("beneish_m_score", {}),
            sloan_accrual=result.established_models.get("sloan_accrual", {}),
            altman_z_score=result.established_models.get("altman_z_score", {}),
            piotroski_f_score=result.established_models.get("piotroski_f_score", {}),
            ohlson_o_score=result.established_models.get("ohlson_o_score", {}),
        )

        # 4. Forensic Findings Schema
        findings_schemas = [
            ForensicFindingSchema(
                rule_id=f.rule_id,
                rule_name=f.rule_name,
                pillar=f.pillar,
                triggered=f.triggered,
                severity=f.severity,
                trigger_condition=f.trigger_condition,
                evidence=f.evidence,
                forensic_finding=f.forensic_finding,
                why_it_matters=f.why_it_matters,
                recommended_investigation=f.recommended_investigation,
                question_for_management=f.question_for_management,
                evidence_state=f.evidence_state,
            )
            for f in result.forensic_findings
        ]

        # 5. Audit Trail Schema
        audit_schema = AuditTrailSchema(
            assessment_id=result.audit_trail.assessment_id,
            analysis_id=result.audit_trail.analysis_id,
            efs_version=result.audit_trail.efs_version,
            scoring_version=result.audit_trail.scoring_version,
            rulebook_version=result.audit_trail.rulebook_version,
            engine_version=result.audit_trail.engine_version,
            timestamp=result.audit_trail.timestamp,
            variables_evaluated=result.audit_trail.variables_evaluated,
            variables_available=result.audit_trail.variables_available,
            rules_evaluated=result.audit_trail.rules_evaluated,
            rules_triggered=result.audit_trail.rules_triggered,
            calculation_time_ms=result.audit_trail.calculation_time_ms,
        )

        return EFSResponse(
            assessment_id=result.assessment_id,
            analysis_id=result.analysis_id,
            efs_version=result.efs_version,
            status=result.status,
            overall=overall_schema,
            pillars=pillar_schemas,
            established_models=models_schema,
            forensic_findings=findings_schemas,
            red_flags=result.red_flags,
            management_questions=result.management_questions,
            limitations=result.limitations,
            audit_trail=audit_schema,
        )
    except EFSEngineError as err:
        logger.warning("EFS domain error for analysis_id=%s: %s", analysis_id, err.message)
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
