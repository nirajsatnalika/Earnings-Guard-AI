"""FastAPI router for EFS™ AI Forensic Narrative endpoint."""

import logging
from fastapi import APIRouter, HTTPException, status

from app.ai.provider import get_narrative_provider
from app.ai.schemas import EFSNarrativeResponse
from app.calculations.efs.engine import EFSEngine
from app.calculations.efs.exceptions.base import EFSEngineError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/efs", tags=["efs-narrative"])

# Shared engine instance
efs_engine = EFSEngine()


@router.post(
    "/{analysis_id}/narrative",
    response_model=EFSNarrativeResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate EFS™ AI Forensic Narrative",
    description=(
        "Retrieves deterministic EFS assessment evidence for analysis_id, "
        "constructs a controlled evidence payload, and executes the AI Forensic "
        "Narrative layer. The AI layer explains backend findings without altering "
        "scores, weights, or rule triggers."
    ),
)
async def generate_ai_narrative(analysis_id: str) -> EFSNarrativeResponse:
    """Generate structured AI Forensic Narrative for the given ``analysis_id``."""
    logger.info("Received POST /api/v1/efs/%s/narrative", analysis_id)
    try:
        # 1. Run deterministic EFS Engine (Single source of truth)
        assessment_result = efs_engine.run(analysis_id=analysis_id, input_payload={})
        
        # Convert dataclass result to dict
        if hasattr(assessment_result, "to_dict"):
            assessment_dict = assessment_result.to_dict()
        elif hasattr(assessment_result, "__dict__"):
            assessment_dict = getattr(assessment_result, "__dict__", {})
        else:
            assessment_dict = dict(assessment_result)

        # 2. Get active narrative provider (Default LLM or Fallback)
        provider = get_narrative_provider()

        # 3. Generate structured narrative
        narrative_response = await provider.generate_narrative(
            analysis_id=analysis_id, assessment_dict=assessment_dict
        )

        return narrative_response

    except EFSEngineError as err:
        logger.warning("EFS domain error during narrative generation for analysis_id=%s: %s", analysis_id, err.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": err.message, "details": err.details},
        )
    except Exception as exc:
        logger.exception("Unexpected error during narrative generation for analysis_id=%s: %s", analysis_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during narrative generation: {str(exc)}",
        )
