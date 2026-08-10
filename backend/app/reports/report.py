"""FastAPI router for EFS™ PDF report generation.

GET /api/v1/efs/{analysis_id}/report

PHASE 5 CHANGE:
This endpoint now retrieves the PERSISTED assessment snapshot from PostgreSQL
and renders the PDF from stored data. It does NOT re-run EFSEngine.run().

If no completed assessment exists for the given analysis_id, returns HTTP 404.
The only path that creates a new assessment is POST /api/v1/efs/{analysis_id}.
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
    WEASYPRINT_ERROR = None
except Exception as err:
    HTML = None
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(err)

from app.database.database import get_db
from app.persistence.assessment_repository import AssessmentRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/efs", tags=["efs-report"])

_repository = AssessmentRepository()

# Jinja2 environment
templates_path = Path(__file__).resolve().parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(searchpath=str(templates_path)),
    autoescape=select_autoescape(["html", "xml"]),
)


@router.get(
    "/{analysis_id}/report",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate PDF report for a persisted EFS™ assessment",
    description=(
        "Renders the persisted EFS assessment snapshot for the provided ``analysis_id`` "
        "as a print-ready PDF. Does NOT re-run the EFS engine. "
        "Requires a completed assessment (POST /api/v1/efs/{analysis_id} first). "
        "Returns 404 if no completed assessment exists."
    ),
)
async def generate_efs_report(
    analysis_id: str,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Generate PDF from persisted assessment snapshot.

    Phase 5: Reads from PostgreSQL snapshot. EFSEngine is NOT re-run.
    """
    # 1. Retrieve persisted assessment snapshot
    snapshot = _repository.get_assessment_snapshot(db, analysis_id)

    if snapshot is None:
        # Check if assessment exists but is not completed
        existing = _repository.get_assessment_by_analysis_id(db, analysis_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Assessment '{analysis_id}' exists but is not yet COMPLETED "
                    f"(status: {existing.assessment_status}). "
                    "Run POST /api/v1/efs/{analysis_id} to complete it first."
                ),
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No completed assessment found for analysis_id='{analysis_id}'. "
                "Run POST /api/v1/efs/{analysis_id} to create and persist an assessment first."
            ),
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

    # 2. Retrieve persisted AI narrative (if any)
    assessment_record = _repository.get_assessment_by_analysis_id(db, analysis_id)
    narrative_res = None
    if assessment_record:
        stored_narrative = _repository.get_latest_narrative(db, assessment_record.id)
        if stored_narrative:
            try:
                from app.ai.schemas import EFSNarrativeResponse
                narrative_res = EFSNarrativeResponse(**stored_narrative.narrative_payload)
            except Exception as narr_err:
                logger.warning("Could not deserialize stored narrative: %s", narr_err)

    # 3. Build a report-compatible object from the snapshot dict
    class _SnapshotView:
        """Minimal view object bridging snapshot dict to Jinja2 template."""
        def __init__(self, d: dict) -> None:
            self.__dict__.update(d)
            # Wrap sub-dicts as objects for template compatibility
            if isinstance(d.get("overall"), dict):
                self.overall = _SnapshotView(d["overall"])
            if isinstance(d.get("established_models"), dict):
                em = d["established_models"]
                self.established_models = {
                    k: _SnapshotView(v) if isinstance(v, dict) else v
                    for k, v in em.items()
                }
            self.pillars = [_SnapshotView(p) for p in d.get("pillars", [])]
            for pillar in self.pillars:
                pillar.variables = [_SnapshotView(v) for v in getattr(pillar, "variables", [])]
            self.forensic_findings = [_SnapshotView(f) for f in d.get("forensic_findings", [])]
            if isinstance(d.get("audit_trail"), dict):
                self.audit_trail = _SnapshotView(d["audit_trail"])
            self.company_name = analysis_id  # Fallback company name
            self.red_flags = d.get("red_flags", [])
            self.management_questions = d.get("management_questions", [])
            self.limitations = d.get("limitations", [])

    result_view = _SnapshotView(snapshot)

    # 4. Render HTML → PDF
    template = jinja_env.get_template("report.html")
    html_content = template.render(
        assessment=result_view,
        narrative=narrative_res,
        generated_at=datetime.utcnow().isoformat() + "Z",
        persisted=True,
        snapshot_hash=snapshot.get("assessment_snapshot_hash"),
    )
    pdf_bytes = HTML(string=html_content).write_pdf()

    # 5. Log report retrieval in audit trail
    try:
        from app.models.assessment_audit_log import AssessmentAuditLog
        import uuid as _uuid
        al = AssessmentAuditLog(
            id=str(_uuid.uuid4()),
            assessment_id=assessment_record.id if assessment_record else "unknown",
            event_type="REPORT_RETRIEVED",
            event_data={"source": "persisted_snapshot", "analysis_id": analysis_id},
        )
        db.add(al)
        db.commit()
    except Exception:
        pass  # Audit log must never block PDF delivery

    # 6. Build filename and stream
    safe_name = "".join(c for c in analysis_id if c.isalnum() or c in "_- ")
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"EFS_Assessment_{safe_name}_{today_str}.pdf"

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
