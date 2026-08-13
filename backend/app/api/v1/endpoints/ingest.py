"""Ingestion API endpoints: POST /api/v1/ingest/{analysis_id} and /confirm"""

from fastapi import APIRouter, HTTPException, status

from app.core.logging import get_logger
from app.schemas.ingest import ConfirmReviewRequest, ConfirmReviewResponse, IngestResponse
from app.services.ingestion_service import IngestionService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/{analysis_id}", response_model=IngestResponse, status_code=200)
async def process_document_ingestion(analysis_id: str) -> IngestResponse:
    """Extract, normalize, map, and construct canonical ingestion review items."""
    logger.info("Ingestion request received for analysis %s", analysis_id)
    try:
        return IngestionService.process_ingestion(analysis_id)
    except Exception as exc:
        logger.error("Ingestion failed for analysis %s: %s", analysis_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest documents: {str(exc)}",
        ) from exc


@router.post("/{analysis_id}/confirm", response_model=ConfirmReviewResponse, status_code=200)
async def confirm_ingestion_review(
    analysis_id: str, request: ConfirmReviewRequest
) -> ConfirmReviewResponse:
    """Confirm human review choices and generate raw_variables payload for EFS engine."""
    logger.info("Confirm review request received for analysis %s with %d item(s)", analysis_id, len(request.items))
    try:
        return IngestionService.confirm_review(analysis_id, request.items)
    except Exception as exc:
        logger.error("Confirm review failed for analysis %s: %s", analysis_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm review: {str(exc)}",
        ) from exc
