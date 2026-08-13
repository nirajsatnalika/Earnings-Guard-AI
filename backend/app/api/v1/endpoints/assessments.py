"""API endpoints for assessment history and retrieval.

GET /api/v1/assessments                     — List all assessments (paginated)
GET /api/v1/assessments/{assessment_id}     — Get assessment detail from persisted snapshot
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.persistence.assessment_repository import AssessmentRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assessments", tags=["assessments"])

_repository = AssessmentRepository()


# ─── Response Schemas ──────────────────────────────────────────────────────────

class AssessmentListItem(BaseModel):
    """Lightweight summary for assessment history list."""
    id: str
    analysis_id: str
    company_id: str
    assessment_status: str
    score_status: str
    overall_score: Optional[float]
    risk_level: Optional[str]
    confidence_score: Optional[float]
    confidence_level: Optional[str]
    rules_triggered: Optional[int]
    variables_evaluated: Optional[int]
    efs_version: str
    methodology_version: str
    created_at: str
    completed_at: Optional[str]
    input_snapshot_hash: Optional[str]
    assessment_snapshot_hash: Optional[str]


class AssessmentListResponse(BaseModel):
    items: List[AssessmentListItem]
    total: int
    page: int
    limit: int


def _assessment_to_list_item(assessment: Any) -> AssessmentListItem:
    return AssessmentListItem(
        id=assessment.id,
        analysis_id=assessment.analysis_id,
        company_id=assessment.company_id,
        assessment_status=assessment.assessment_status,
        score_status=assessment.score_status,
        overall_score=assessment.overall_score,
        risk_level=assessment.risk_level,
        confidence_score=assessment.confidence_score,
        confidence_level=assessment.confidence_level,
        rules_triggered=assessment.rules_triggered,
        variables_evaluated=assessment.variables_evaluated,
        efs_version=assessment.efs_version,
        methodology_version=assessment.methodology_version,
        created_at=assessment.created_at.isoformat(),
        completed_at=assessment.completed_at.isoformat() if assessment.completed_at else None,
        input_snapshot_hash=assessment.input_snapshot_hash,
        assessment_snapshot_hash=assessment.assessment_snapshot_hash,
    )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=AssessmentListResponse,
    summary="List all assessments (assessment history)",
)
async def list_assessments(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> AssessmentListResponse:
    """Return paginated assessment history, most recent first."""
    offset = (page - 1) * limit
    assessments = _repository.list_assessments(db, limit=limit, offset=offset)
    total = _repository.count_assessments(db)
    return AssessmentListResponse(
        items=[_assessment_to_list_item(a) for a in assessments],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{assessment_id}",
    summary="Get assessment detail from persisted snapshot",
)
async def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Return the full persisted assessment snapshot by assessment UUID.

    Reads from DB snapshot. Does NOT re-run EFSEngine.
    Returns HTTP 404 if assessment not found or not yet completed.
    """
    assessment = _repository.get_assessment_by_id(db, assessment_id) or _repository.get_assessment_by_analysis_id(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment '{assessment_id}' not found.",
        )
    if assessment.assessment_status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Assessment '{assessment_id}' is not yet COMPLETED "
                f"(status: {assessment.assessment_status})."
            ),
        )

    snapshot = _repository.get_assessment_snapshot(db, assessment.analysis_id)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Assessment record exists but snapshot reconstruction failed.",
        )
    return snapshot
