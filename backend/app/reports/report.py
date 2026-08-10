"""FastAPI router for PDF report generation"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
    WEASYPRINT_ERROR = None
except Exception as err:
    HTML = None
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(err)

logger = logging.getLogger(__name__)

from app.calculations.efs.engine import EFSEngine
from app.calculations.efs.exceptions.base import EFSEngineError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/efs", tags=["efs-report"])

# Shared engine instance (same as calculation endpoint)
efs_engine = EFSEngine()

# Jinja2 environment – templates directory located at backend/app/templates
templates_path = Path(__file__).resolve().parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(searchpath=str(templates_path)),
    autoescape=select_autoescape(["html", "xml"]),
)

@router.get(
    "/{analysis_id}/report",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate PDF report for an EFS™ assessment",
    description=(
        "Renders the deterministic EFS assessment for the provided ``analysis_id`` "
        "as a print‑ready PDF using a Jinja2 template and WeasyPrint. "
        "No new calculations are performed – the response mirrors the JSON "
        "assessment payload."
    ),
)
async def generate_efs_report(analysis_id: str) -> StreamingResponse:
    """Generate a PDF report for the given ``analysis_id``.

    1. Run the deterministic engine (same logic as the JSON endpoint).
    2. Render an HTML template populated with the assessment data.
    3. Convert the HTML to PDF via WeasyPrint.
    4. Stream the PDF back with a descriptive filename.
    """
    try:
        result = efs_engine.run(analysis_id=analysis_id, input_payload={})
    except EFSEngineError as err:
        logger.warning("EFS domain error for analysis_id=%s: %s", analysis_id, err.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": err.message, "details": err.details},
        )
    except Exception as exc:
        logger.exception("Unexpected error during EFS report generation for analysis_id=%s", analysis_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during EFS report generation: {str(exc)}",
        )

    if not WEASYPRINT_AVAILABLE:
        logger.error("WeasyPrint is unavailable: %s", WEASYPRINT_ERROR)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "PDF generation is currently unavailable on this environment because "
                "WeasyPrint system C-libraries (GTK/Pango/Cairo) are missing. "
                f"Original error: {WEASYPRINT_ERROR}"
            ),
        )

    # Generate narrative explanation using active provider or fallback
    try:
        from app.ai.provider import get_narrative_provider
        provider = get_narrative_provider()
        res_dict = result.to_dict() if hasattr(result, "to_dict") else getattr(result, "__dict__", {})
        narrative_res = await provider.generate_narrative(analysis_id=analysis_id, assessment_dict=res_dict)
    except Exception as n_err:
        logger.warning("Could not generate AI narrative for report: %s", n_err)
        narrative_res = None

    template = jinja_env.get_template("report.html")
    html_content = template.render(
        assessment=result,
        narrative=narrative_res,
        generated_at=datetime.utcnow().isoformat() + "Z",
    )
    pdf_bytes = HTML(string=html_content).write_pdf()

    # Build a safe filename
    company_name = getattr(result, "company_name", "Company")
    safe_company = "".join(c for c in company_name if c.isalnum() or c in "_- ")
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"EFS_Assessment_{safe_company}_{today_str}.pdf"

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
