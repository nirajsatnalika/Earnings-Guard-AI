"""FastAPI router for EFS™ AI Forensic Narrative endpoint.

POST /api/v1/efs/{analysis_id}/narrative

PHASE 5 CHANGE:
1. Retrieve persisted assessment from DB (does NOT re-run EFSEngine).
2. Use stored deterministic evidence to build the narrative evidence payload.
3. Generate AI narrative via provider.
4. Persist narrative to DB.
5. Return EFSNarrativeResponse.

AI must NEVER mutate deterministic assessment records.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.provider import get_narrative_provider
from app.ai.schemas import EFSNarrativeResponse
from app.database.database import get_db
from app.persistence.assessment_repository import AssessmentRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/efs", tags=["efs-narrative"])

_repository = AssessmentRepository()


@router.post(
    "/{analysis_id}/narrative",
    response_model=EFSNarrativeResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate EFS™ AI Forensic Narrative (from persisted assessment)",
    description=(
        "Retrieves the persisted deterministic EFS assessment evidence for analysis_id, "
        "constructs a controlled evidence payload, and executes the AI Forensic Narrative layer. "
        "Does NOT re-run the EFS engine. Requires a completed assessment. "
        "The AI layer explains backend findings without altering scores, weights, or rule triggers."
    ),
)
async def generate_ai_narrative(
    analysis_id: str,
    db: Session = Depends(get_db),
) -> EFSNarrativeResponse:
    """Generate and persist AI Forensic Narrative for the given analysis_id."""
    logger.info("Received POST /api/v1/efs/%s/narrative", analysis_id)

    # 1. Retrieve persisted assessment snapshot (do NOT re-run engine)
    snapshot = _repository.get_assessment_snapshot(db, analysis_id)

    if snapshot is None:
        existing = _repository.get_assessment_by_analysis_id(db, analysis_id)
        if existing and existing.assessment_status != "COMPLETED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Assessment '{analysis_id}' exists but is not COMPLETED "
                    f"(status: {existing.assessment_status}). Complete it first."
                ),
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No completed assessment found for analysis_id='{analysis_id}'. "
                "Run POST /api/v1/efs/{analysis_id} first."
            ),
        )

    assessment_record = _repository.get_assessment_by_analysis_id(db, analysis_id)

    # 2. Check if a narrative already exists — return stored one if present
    if assessment_record:
        existing_narrative = _repository.get_latest_narrative(db, assessment_record.id)
        if existing_narrative and existing_narrative.status in ("COMPLETED", "FALLBACK"):
            try:
                narrative_response = EFSNarrativeResponse(**existing_narrative.narrative_payload)
                logger.info(
                    "Returning persisted narrative for analysis_id=%s (status=%s)",
                    analysis_id, existing_narrative.status,
                )
                return narrative_response
            except Exception as deser_err:
                logger.warning("Could not deserialize stored narrative, regenerating: %s", deser_err)

    # 3. Generate AI narrative from stored evidence (not re-running engine)
    try:
        provider = get_narrative_provider()
        narrative_response = await provider.generate_narrative(
            analysis_id=analysis_id, assessment_dict=snapshot
        )
    except Exception as exc:
        logger.exception("Narrative generation failed for analysis_id=%s: %s", analysis_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during narrative generation: {str(exc)}",
        )

    # 4. Persist narrative (must not alter deterministic assessment)
    if assessment_record:
        try:
            provider_info = getattr(narrative_response, "provider_info", {}) or {}
            is_fallback = provider_info.get("fallback_used", True)
            narrative_status = "FALLBACK" if is_fallback else "COMPLETED"
            _repository.persist_narrative(db, assessment_record, narrative_response, provider_status=narrative_status)
            db.commit()
        except Exception as persist_err:
            logger.warning("Failed to persist narrative for analysis_id=%s: %s", analysis_id, persist_err)
            try:
                db.rollback()
            except Exception:
                pass

    return narrative_response
