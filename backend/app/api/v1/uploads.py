"""Upload endpoint for financial statements."""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.upload import UploadResponse
from app.services.upload_service import UploadService, UploadValidationError

router = APIRouter(prefix="/api/v1/upload")

UPLOAD_ROOT = Path(__file__).resolve().parents[3] / "uploads"


@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload financial statements",
)
def upload_financial_statements(
    balance_sheet: UploadFile = File(..., description="Balance Sheet (.xlsx, .xls, or .csv)"),
    profit_loss: UploadFile = File(..., description="Profit & Loss Statement (.xlsx, .xls, or .csv)"),
    cash_flow: UploadFile = File(..., description="Cash Flow Statement (.xlsx, .xls, or .csv)"),
) -> UploadResponse:
    """Validate and store the three financial statement files for an analysis."""
    analysis_id = uuid4()
    service = UploadService(UPLOAD_ROOT)
    try:
        uploaded_files = service.save_statement_files(
            analysis_id,
            files=(
                ("Balance Sheet", balance_sheet),
                ("Profit & Loss Statement", profit_loss),
                ("Cash Flow Statement", cash_flow),
            ),
        )
    except UploadValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Uploaded files could not be stored",
        ) from exc

    return UploadResponse(
        analysis_id=str(analysis_id),
        status="uploaded",
        uploaded_files=uploaded_files,
    )
