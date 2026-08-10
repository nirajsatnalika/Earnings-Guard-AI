"""API endpoints for company management.

POST /api/v1/companies              — Create a company record
GET  /api/v1/companies              — List all companies
GET  /api/v1/companies/{company_id} — Get a single company
GET  /api/v1/companies/{company_id}/assessments — List company assessments
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.persistence.assessment_repository import AssessmentRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/companies", tags=["companies"])

_repository = AssessmentRepository()


# ─── Request / Response schemas ───────────────────────────────────────────────

class CompanyCreateRequest(BaseModel):
    legal_name: str = Field(..., min_length=1, max_length=512)
    display_name: Optional[str] = Field(None, max_length=512)
    ticker: Optional[str] = Field(None, max_length=32)
    exchange: Optional[str] = Field(None, max_length=64)
    country: Optional[str] = Field(None, max_length=128)
    industry: Optional[str] = Field(None, max_length=256)


class CompanyResponse(BaseModel):
    id: str
    legal_name: str
    display_name: Optional[str]
    ticker: Optional[str]
    exchange: Optional[str]
    country: Optional[str]
    industry: Optional[str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class AssessmentSummary(BaseModel):
    id: str
    analysis_id: str
    assessment_status: str
    score_status: str
    overall_score: Optional[float]
    risk_level: Optional[str]
    confidence_score: Optional[float]
    confidence_level: Optional[str]
    rules_triggered: Optional[int]
    variables_evaluated: Optional[int]
    efs_version: str
    created_at: str
    completed_at: Optional[str]
    input_snapshot_hash: Optional[str]
    assessment_snapshot_hash: Optional[str]

    model_config = {"from_attributes": True}


def _company_to_response(company: Any) -> CompanyResponse:
    return CompanyResponse(
        id=company.id,
        legal_name=company.legal_name,
        display_name=company.display_name,
        ticker=company.ticker,
        exchange=company.exchange,
        country=company.country,
        industry=company.industry,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )


def _assessment_to_summary(assessment: Any) -> AssessmentSummary:
    return AssessmentSummary(
        id=assessment.id,
        analysis_id=assessment.analysis_id,
        assessment_status=assessment.assessment_status,
        score_status=assessment.score_status,
        overall_score=assessment.overall_score,
        risk_level=assessment.risk_level,
        confidence_score=assessment.confidence_score,
        confidence_level=assessment.confidence_level,
        rules_triggered=assessment.rules_triggered,
        variables_evaluated=assessment.variables_evaluated,
        efs_version=assessment.efs_version,
        created_at=assessment.created_at.isoformat(),
        completed_at=assessment.completed_at.isoformat() if assessment.completed_at else None,
        input_snapshot_hash=assessment.input_snapshot_hash,
        assessment_snapshot_hash=assessment.assessment_snapshot_hash,
    )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a company record",
)
async def create_company(
    body: CompanyCreateRequest,
    db: Session = Depends(get_db),
) -> CompanyResponse:
    """Create a new company entity."""
    company = _repository.create_company(
        db,
        legal_name=body.legal_name,
        display_name=body.display_name,
        ticker=body.ticker,
        exchange=body.exchange,
        country=body.country,
        industry=body.industry,
    )
    db.commit()
    return _company_to_response(company)


@router.get(
    "",
    response_model=List[CompanyResponse],
    summary="List all companies",
)
async def list_companies(
    db: Session = Depends(get_db),
) -> List[CompanyResponse]:
    """List all companies, most recently created first."""
    companies = _repository.list_companies(db)
    return [_company_to_response(c) for c in companies]


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get a company by ID",
)
async def get_company(
    company_id: str,
    db: Session = Depends(get_db),
) -> CompanyResponse:
    """Get a single company by its UUID."""
    company = _repository.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{company_id}' not found.",
        )
    return _company_to_response(company)


@router.get(
    "/{company_id}/assessments",
    response_model=List[AssessmentSummary],
    summary="List all assessments for a company",
)
async def get_company_assessments(
    company_id: str,
    db: Session = Depends(get_db),
) -> List[AssessmentSummary]:
    """List all assessments for a given company, most recent first."""
    company = _repository.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{company_id}' not found.",
        )
    assessments = _repository.get_company_assessments(db, company_id)
    return [_assessment_to_summary(a) for a in assessments]
