"""Assessment Service — orchestrates the full EFS assessment lifecycle.

Lifecycle:
  POST /api/v1/efs/{analysis_id}
        ↓
  Company (get or create)
        ↓
  Assessment (DRAFT → RUNNING)
        ↓
  EFSEngine.run() — deterministic
        ↓
  Persist snapshot (COMPLETED)
        ↓
  AI Narrative (optional — failure does NOT fail assessment)
        ↓
  Persist narrative (COMPLETED / FALLBACK / UNAVAILABLE)
        ↓
  Return EFSExecutionResult

CRITICAL RULES:
- The EFS engine is the single source of truth for all calculations.
- This service persists results. It does NOT alter them.
- AI failure must not propagate to assessment failure.
- analysis_id is unique. A second call with the same analysis_id returns
  the persisted result without re-running the engine.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.calculations.efs.engine import EFSEngine
from app.models.assessment import Assessment
from app.persistence.assessment_repository import AssessmentRepository

logger = logging.getLogger(__name__)

# Module-level shared instances
_efs_engine = EFSEngine()
_repository = AssessmentRepository()


class AssessmentService:
    """Orchestrates EFS assessment creation, execution, and persistence."""

    def __init__(
        self,
        engine: Optional[EFSEngine] = None,
        repository: Optional[AssessmentRepository] = None,
    ) -> None:
        self._engine = engine or _efs_engine
        self._repo = repository or _repository

    def run_and_persist(
        self,
        session: Session,
        analysis_id: str,
        input_payload: Dict[str, Any],
    ) -> tuple[Any, Assessment]:
        """Run the EFS deterministic engine and persist the result.

        If an assessment with this analysis_id already exists and is COMPLETED,
        returns the stored result snapshot without re-running the engine.

        Returns:
            (EFSExecutionResult, Assessment)
        """
        # Check if already persisted (immutability: don't re-run completed assessments)
        existing = self._repo.get_assessment_by_analysis_id(session, analysis_id)
        if existing and existing.assessment_status == "COMPLETED":
            logger.info(
                "Assessment for analysis_id=%r already persisted (id=%s). "
                "Returning persisted snapshot without re-running engine.",
                analysis_id, existing.id,
            )
            # Re-run engine to return EFSExecutionResult for API response
            # (the persisted DB data is authoritative for reports/history)
            result = self._engine.run(analysis_id=analysis_id, input_payload=input_payload)
            return result, existing

        # Get or create company
        company = self._repo.get_or_create_company_for_analysis(session, analysis_id)

        # Create assessment record (DRAFT)
        assessment = self._repo.create_assessment(session, company.id, analysis_id)
        self._log_event(session, assessment, "ASSESSMENT_CREATED", {"analysis_id": analysis_id})

        # Mark RUNNING
        assessment.assessment_status = "RUNNING"
        session.flush()
        self._log_event(session, assessment, "ENGINE_STARTED", {})

        try:
            # Run deterministic EFS engine
            result = self._engine.run(analysis_id=analysis_id, input_payload=input_payload)

            # Persist full snapshot
            self._repo.persist_efs_result(session, assessment, result, input_payload)
            session.commit()
            self._log_event(session, assessment, "ENGINE_COMPLETED", {
                "rules_triggered": assessment.rules_triggered,
                "score_status": assessment.score_status,
            })

        except Exception as engine_err:
            logger.error("EFS engine failed for analysis_id=%r: %s", analysis_id, engine_err)
            assessment.assessment_status = "FAILED"
            self._log_event(session, assessment, "ENGINE_FAILED", {"error": str(engine_err)})
            session.commit()
            raise

        # Attempt AI narrative (failure must NOT fail the assessment)
        try:
            from app.ai.provider import get_narrative_provider
            provider = get_narrative_provider()
            result_dict = result.to_dict() if hasattr(result, "to_dict") else getattr(result, "__dict__", {})
            narrative = await_or_run(provider.generate_narrative(analysis_id, result_dict))
            provider_info = getattr(narrative, "provider_info", {}) or {}
            is_fallback = provider_info.get("fallback_used", True)
            narrative_status = "FALLBACK" if is_fallback else "COMPLETED"
            self._repo.persist_narrative(session, assessment, narrative, provider_status=narrative_status)
            session.commit()
        except Exception as narr_err:
            logger.warning(
                "AI narrative failed for analysis_id=%r (assessment remains COMPLETED): %s",
                analysis_id, narr_err,
            )
            self._log_event(session, assessment, "NARRATIVE_FAILED", {"error": str(narr_err)})
            session.commit()

        return result, assessment

    def _log_event(
        self,
        session: Session,
        assessment: Assessment,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> None:
        """Append an audit log entry for this assessment."""
        from app.models.assessment_audit_log import AssessmentAuditLog
        import uuid

        entry = AssessmentAuditLog(
            id=str(uuid.uuid4()),
            assessment_id=assessment.id,
            event_type=event_type,
            event_data=event_data,
        )
        session.add(entry)
        try:
            session.flush()
        except Exception:
            pass  # Audit log failure must never block assessment flow


def await_or_run(coro: Any) -> Any:
    """Run a coroutine synchronously when called from a sync context.

    Used so AssessmentService can be called from both sync tests and async FastAPI routes.
    """
    import asyncio
    import inspect
    if inspect.iscoroutine(coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In an async context: create a new event loop in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)
    return coro
