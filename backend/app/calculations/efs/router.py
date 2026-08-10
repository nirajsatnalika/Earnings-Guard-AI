"""FastAPI router for EFS™ Assessment Engine endpoints.

POST /api/v1/efs/{analysis_id}  — Run EFS engine and persist assessment snapshot.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
from app.database.database import get_db
from app.persistence.assessment_repository import AssessmentRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/efs", tags=["efs"])

# Shared engine and repository instances
efs_engine = EFSEngine()
_repository = AssessmentRepository()


@router.post(
    "/{analysis_id}",
    response_model=EFSResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Earnings Financial Safety (EFS™) Forensic Assessment",
    description="Methodology-driven deterministic engine evaluating financial statement quality across 7 pillars. Results are persisted as an immutable snapshot.",
)
async def calculate_efs(
    analysis_id: str,
    payload: EFSRequest = EFSRequest(),
    db: Session = Depends(get_db),
) -> EFSResponse:
    """POST endpoint executing EFS forensic assessment for a given analysis_id.

    Runs the deterministic engine and persists the result snapshot.
    If a completed assessment already exists for this analysis_id, returns
    the previously persisted snapshot without re-running the engine.
    """
    logger.info("Received POST /api/v1/efs/%s", analysis_id)
    try:
        input_data = payload.model_dump(exclude_none=True)

        # Run deterministic EFS engine
        result = efs_engine.run(analysis_id=analysis_id, input_payload=input_data)

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

    # Persist snapshot (non-blocking — assessment API response is not affected by persistence failures)
    try:
        existing = _repository.get_assessment_by_analysis_id(db, analysis_id)
        if not existing or existing.assessment_status != "COMPLETED":
            from app.models.company import Company
            import uuid
            # Get or create company
            company = _repository.get_or_create_company_for_analysis(db, analysis_id)
            if not existing:
                assessment = _repository.create_assessment(db, company.id, analysis_id)
            else:
                assessment = existing
            assessment.assessment_status = "RUNNING"
            db.flush()
            _repository.persist_efs_result(db, assessment, result, input_data)
            db.commit()
            logger.info("Persisted assessment snapshot for analysis_id=%s", analysis_id)
        else:
            logger.info("Assessment for analysis_id=%s already persisted. Skipping re-persist.", analysis_id)
    except Exception as persist_err:
        logger.warning(
            "Persistence failed for analysis_id=%s (assessment result still returned): %s",
            analysis_id, persist_err,
        )
        try:
            db.rollback()
        except Exception:
            pass

    # Build API response (unchanged from original)
    overall_schema = OverallSchema(
        score=result.overall.score,
        score_status=result.overall.score_status,
        risk_level=result.overall.risk_level,
        confidence=result.overall.confidence,
    )

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

    models_schema = EstablishedModelsSchema(
        beneish_m_score=result.established_models.get("beneish_m_score", {}),
        sloan_accrual=result.established_models.get("sloan_accrual", {}),
        altman_z_score=result.established_models.get("altman_z_score", {}),
        piotroski_f_score=result.established_models.get("piotroski_f_score", {}),
        ohlson_o_score=result.established_models.get("ohlson_o_score", {}),
    )

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
