"""Assessment Repository — persistence layer for EarningsGuard™ AI.

Handles all CRUD operations for companies, assessments, and all child
snapshot tables. The repository layer is the only layer that touches
the database. It never calls EFSEngine or AI providers.

IMMUTABILITY CONTRACT:
A COMPLETED assessment snapshot must never be overwritten.
Creating a new assessment for the same company creates a new row.
The analysis_id must be unique — attempting to persist a duplicate
analysis_id raises an integrity error (handled in service layer).
"""

import dataclasses
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.assessment_audit_log import AssessmentAuditLog
from app.models.assessment_confidence import AssessmentConfidence
from app.models.assessment_finding import AssessmentFinding
from app.models.assessment_input import AssessmentInput
from app.models.assessment_management_question import AssessmentManagementQuestion
from app.models.assessment_model import AssessmentModel
from app.models.assessment_narrative import AssessmentNarrative
from app.models.assessment_pillar import AssessmentPillar
from app.models.assessment_red_flag import AssessmentRedFlag
from app.models.assessment_variable import AssessmentVariable
from app.models.company import Company
from app.persistence.snapshot_hasher import hash_assessment_snapshot, hash_input_snapshot

logger = logging.getLogger(__name__)


def _safe_dict(obj: Any) -> Any:
    """Convert dataclass or arbitrary object to a JSON-safe dict."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return obj


class AssessmentRepository:
    """All database operations for the EFS assessment persistence layer."""

    # ─── Company Operations ───────────────────────────────────────────────────

    def create_company(
        self,
        session: Session,
        legal_name: str,
        display_name: Optional[str] = None,
        ticker: Optional[str] = None,
        exchange: Optional[str] = None,
        country: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> Company:
        """Create and persist a new company record."""
        company = Company(
            id=str(uuid.uuid4()),
            legal_name=legal_name,
            display_name=display_name or legal_name,
            ticker=ticker,
            exchange=exchange,
            country=country,
            industry=industry,
        )
        session.add(company)
        session.flush()
        logger.info("Created company id=%s name=%r", company.id, company.legal_name)
        return company

    def get_or_create_company_for_analysis(
        self, session: Session, analysis_id: str
    ) -> Company:
        """Return an existing company or auto-create a minimal one from the analysis_id.

        For Phase 5, companies are auto-provisioned from the analysis_id string
        so the existing assessment flow continues to work without a separate
        company creation step.
        """
        # Derive a human-readable name from the analysis_id
        display = analysis_id.replace("_", " ").title()
        # Attempt to find an existing assessment with this analysis_id
        existing = session.query(Assessment).filter_by(analysis_id=analysis_id).first()
        if existing:
            company = session.get(Company, existing.company_id)
            if company:
                return company
        # Create a new minimal company record
        return self.create_company(session, legal_name=display, display_name=display)

    def get_company(self, session: Session, company_id: str) -> Optional[Company]:
        """Get a company by primary key."""
        return session.get(Company, company_id)

    def list_companies(self, session: Session) -> List[Company]:
        """List all companies, most recently created first."""
        return session.query(Company).order_by(Company.created_at.desc()).all()

    # ─── Assessment Operations ────────────────────────────────────────────────

    def create_assessment(
        self,
        session: Session,
        company_id: str,
        analysis_id: str,
    ) -> Assessment:
        """Create a new assessment record in DRAFT status."""
        assessment = Assessment(
            id=str(uuid.uuid4()),
            company_id=company_id,
            analysis_id=analysis_id,
            assessment_status="DRAFT",
            score_status="CALIBRATION_PENDING",
        )
        session.add(assessment)
        session.flush()
        logger.info("Created assessment id=%s analysis_id=%r", assessment.id, analysis_id)
        return assessment

    def get_assessment_by_id(self, session: Session, assessment_id: str) -> Optional[Assessment]:
        """Get assessment by primary key."""
        return session.get(Assessment, assessment_id)

    def get_assessment_by_analysis_id(
        self, session: Session, analysis_id: str
    ) -> Optional[Assessment]:
        """Get assessment by external analysis_id."""
        return session.query(Assessment).filter_by(analysis_id=analysis_id).first()

    def list_assessments(
        self,
        session: Session,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Assessment]:
        """List all assessments, most recently created first."""
        return (
            session.query(Assessment)
            .order_by(Assessment.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_assessments(self, session: Session) -> int:
        """Return total assessment count."""
        return session.query(Assessment).count()

    def get_company_assessments(
        self, session: Session, company_id: str
    ) -> List[Assessment]:
        """Get all assessments for a company, most recent first."""
        return (
            session.query(Assessment)
            .filter_by(company_id=company_id)
            .order_by(Assessment.created_at.desc())
            .all()
        )

    # ─── Snapshot Persistence ─────────────────────────────────────────────────

    def persist_efs_result(
        self,
        session: Session,
        assessment: Assessment,
        result: Any,
        input_payload: Dict[str, Any],
    ) -> None:
        """Persist the full EFS deterministic assessment result as an immutable snapshot.

        This method:
        1. Computes input_snapshot_hash and assessment_snapshot_hash server-side.
        2. Stores all child records (variables, pillars, models, findings, etc.).
        3. Updates the assessment record to COMPLETED.

        DOES NOT modify any EFS calculation result.
        Hashes are audit metadata only.
        """
        # 1. Compute snapshot hashes (audit integrity metadata)
        input_hash = hash_input_snapshot(input_payload)

        # Build a serializable dict of the assessment result for hashing
        result_dict = _build_result_dict_for_hashing(result)
        snapshot_hash = hash_assessment_snapshot(result_dict)

        # 2. Persist AssessmentInput
        ai_record = AssessmentInput(
            id=str(uuid.uuid4()),
            assessment_id=assessment.id,
            input_payload=input_payload,
            source_metadata={"analysis_id": result.analysis_id, "efs_version": result.efs_version},
        )
        session.add(ai_record)

        # 3. Persist AssessmentVariables (all 95)
        for pillar in result.pillars:
            for var in pillar.variables:
                av = AssessmentVariable(
                    id=str(uuid.uuid4()),
                    assessment_id=assessment.id,
                    variable_id=var.variable_id,
                    variable_name=var.variable_name,
                    pillar=var.pillar,
                    raw_value=var.raw_value,
                    score=var.score,
                    scoring_band=var.scoring_band,
                    unit=var.unit,
                    status=var.data_status,
                    evidence_state=var.calculation_status,
                    source_fields=list(var.source_fields) if var.source_fields else [],
                    calculation_source=var.calculation_status,
                )
                session.add(av)

        # 4. Persist AssessmentPillars (7 pillars)
        for pillar in result.pillars:
            ap = AssessmentPillar(
                id=str(uuid.uuid4()),
                assessment_id=assessment.id,
                pillar_id=pillar.pillar_id,
                pillar_name=pillar.pillar_name,
                pillar_score=pillar.pillar_score,
                status=pillar.status,
                variables_evaluated=pillar.variables_evaluated,
                variables_available=pillar.variables_available,
                positive_drivers=list(pillar.key_positive_drivers),
                negative_drivers=list(pillar.key_negative_drivers),
                data_quality=getattr(pillar, "data_quality", None),
            )
            session.add(ap)

        # 5. Persist AssessmentModels (5 established models)
        for model_key, model_data in result.established_models.items():
            if not isinstance(model_data, dict):
                model_data = _safe_dict(model_data)
            am = AssessmentModel(
                id=str(uuid.uuid4()),
                assessment_id=assessment.id,
                model_name=model_data.get("model_name", model_key),
                model_role=model_data.get("role", model_data.get("model_role")),
                result=model_data,
                signal=str(model_data.get("risk_signal", model_data.get("signal", ""))),
                interpretation=model_data.get("interpretation", ""),
                components=model_data.get("components", model_data.get("signals", {})),
            )
            session.add(am)

        # 6. Persist AssessmentFindings (all 110 rules)
        for finding in result.forensic_findings:
            ev = finding.evidence if isinstance(finding.evidence, dict) else {"text": str(finding.evidence)}
            af = AssessmentFinding(
                id=str(uuid.uuid4()),
                assessment_id=assessment.id,
                rule_id=finding.rule_id,
                rule_name=finding.rule_name,
                pillar=finding.pillar,
                severity=finding.severity,
                triggered=finding.triggered,
                trigger_condition=finding.trigger_condition,
                finding=finding.forensic_finding,
                why_it_matters=finding.why_it_matters,
                evidence=ev,
                audit_procedure=finding.recommended_investigation,
                management_question=finding.question_for_management,
                evidence_state=finding.evidence_state,
            )
            session.add(af)

        # 7. Persist AssessmentRedFlags
        for i, flag_text in enumerate(result.red_flags):
            rf = AssessmentRedFlag(
                id=str(uuid.uuid4()),
                assessment_id=assessment.id,
                severity="High",
                finding=flag_text,
            )
            session.add(rf)

        # 8. Persist AssessmentManagementQuestions
        for i, question in enumerate(result.management_questions):
            mq = AssessmentManagementQuestion(
                id=str(uuid.uuid4()),
                assessment_id=assessment.id,
                question=question,
                priority=i + 1,
            )
            session.add(mq)

        # 9. Persist AssessmentConfidence
        ac = AssessmentConfidence(
            id=str(uuid.uuid4()),
            assessment_id=assessment.id,
            confidence_score=result.overall.confidence,
            confidence_level=_confidence_level(result.overall.confidence),
            factors={},
            limitations=list(result.limitations) if result.limitations else [],
        )
        session.add(ac)

        # 10. Update Assessment record to COMPLETED
        assessment.assessment_status = "COMPLETED"
        assessment.score_status = result.overall.score_status
        assessment.overall_score = result.overall.score  # NULL if CALIBRATION_PENDING
        assessment.risk_level = result.overall.risk_level  # NULL if CALIBRATION_PENDING
        assessment.confidence_score = result.overall.confidence
        assessment.confidence_level = _confidence_level(result.overall.confidence)
        assessment.efs_version = result.efs_version
        assessment.rules_triggered = sum(1 for f in result.forensic_findings if f.triggered)
        assessment.variables_evaluated = sum(p.variables_evaluated for p in result.pillars)
        assessment.input_snapshot_hash = input_hash
        assessment.assessment_snapshot_hash = snapshot_hash
        assessment.completed_at = datetime.now(timezone.utc)

        # 11. Audit log entry
        al = AssessmentAuditLog(
            id=str(uuid.uuid4()),
            assessment_id=assessment.id,
            execution_id=result.audit_trail.assessment_id,
            event_type="SNAPSHOT_PERSISTED",
            event_data={
                "efs_version": result.efs_version,
                "score_status": result.overall.score_status,
                "rules_triggered": assessment.rules_triggered,
                "input_snapshot_hash": input_hash,
                "assessment_snapshot_hash": snapshot_hash,
                "calculation_time_ms": result.audit_trail.calculation_time_ms,
            },
        )
        session.add(al)
        session.flush()

        logger.info(
            "Persisted assessment snapshot id=%s analysis_id=%r "
            "input_hash=%.8s... assessment_hash=%.8s...",
            assessment.id,
            assessment.analysis_id,
            input_hash,
            snapshot_hash,
        )

    def persist_narrative(
        self,
        session: Session,
        assessment: Assessment,
        narrative: Any,
        provider_status: str = "FALLBACK",
    ) -> AssessmentNarrative:
        """Persist an AI narrative alongside its parent assessment.

        AI narrative is stored SEPARATELY from deterministic data.
        It does NOT mutate any assessment field.
        """
        provider_info = getattr(narrative, "provider_info", {}) or {}
        payload = narrative.model_dump() if hasattr(narrative, "model_dump") else _safe_dict(narrative)

        an = AssessmentNarrative(
            id=str(uuid.uuid4()),
            assessment_id=assessment.id,
            narrative_version=getattr(narrative, "narrative_version", "1.0"),
            provider=provider_info.get("provider", "fallback"),
            model=provider_info.get("model", "rule-based-synthesizer"),
            prompt_version="1.0",
            narrative_payload=payload,
            status=provider_status,
        )
        session.add(an)

        # Audit log
        al = AssessmentAuditLog(
            id=str(uuid.uuid4()),
            assessment_id=assessment.id,
            event_type="NARRATIVE_GENERATED" if provider_status == "COMPLETED" else f"NARRATIVE_{provider_status}",
            event_data={"provider": an.provider, "status": provider_status},
        )
        session.add(al)
        session.flush()

        logger.info(
            "Persisted narrative for assessment id=%s provider=%r status=%s",
            assessment.id, an.provider, provider_status,
        )
        return an

    def get_latest_narrative(
        self, session: Session, assessment_id: str
    ) -> Optional[AssessmentNarrative]:
        """Return the most recently generated narrative for an assessment."""
        return (
            session.query(AssessmentNarrative)
            .filter_by(assessment_id=assessment_id)
            .order_by(AssessmentNarrative.generated_at.desc())
            .first()
        )

    # ─── Snapshot Reconstruction ──────────────────────────────────────────────

    def get_assessment_snapshot(
        self, session: Session, analysis_id: str
    ) -> Optional[Dict[str, Any]]:
        """Reconstruct the full EFSResponse-compatible dict from persisted DB rows.

        Returns None if no completed assessment exists for the analysis_id.
        This is the method used by the report endpoint to avoid re-running EFSEngine.
        """
        assessment = self.get_assessment_by_analysis_id(session, analysis_id)
        if not assessment or assessment.assessment_status != "COMPLETED":
            return None

        # Reconstruct variables grouped by pillar
        variables_by_pillar: Dict[str, list] = {}
        for v in assessment.variables:
            variables_by_pillar.setdefault(v.pillar, []).append({
                "variable_id": v.variable_id,
                "variable_name": v.variable_name,
                "pillar": v.pillar,
                "raw_value": v.raw_value,
                "unit": v.unit or "",
                "score": v.score,
                "scoring_band": v.scoring_band,
                "data_status": v.status,
                "source_fields": v.source_fields or [],
                "calculation_status": v.evidence_state,
            })

        # Pillars
        pillars = []
        for p in assessment.pillars:
            pillars.append({
                "pillar_id": p.pillar_id,
                "pillar_name": p.pillar_name,
                "pillar_score": p.pillar_score,
                "variables_evaluated": p.variables_evaluated,
                "variables_available": p.variables_available,
                "variables_missing": [],
                "key_positive_drivers": p.positive_drivers or [],
                "key_negative_drivers": p.negative_drivers or [],
                "data_quality": p.data_quality or "LOW",
                "status": p.status,
                "variables": variables_by_pillar.get(p.pillar_name, []),
            })

        # Established models
        established_models: Dict[str, Any] = {}
        model_key_map = {
            "Beneish M-Score": "beneish_m_score",
            "Sloan Accrual": "sloan_accrual",
            "Altman Z-Score": "altman_z_score",
            "Piotroski F-Score": "piotroski_f_score",
            "Ohlson O-Score": "ohlson_o_score",
        }
        for m in assessment.models:
            key = model_key_map.get(m.model_name, m.model_name.lower().replace(" ", "_").replace("-", "_"))
            established_models[key] = m.result

        # Forensic findings
        findings = []
        for f in assessment.findings:
            findings.append({
                "rule_id": f.rule_id,
                "rule_name": f.rule_name,
                "pillar": f.pillar or "",
                "triggered": f.triggered,
                "severity": f.severity,
                "trigger_condition": f.trigger_condition or "",
                "evidence": f.evidence.get("text", "") if isinstance(f.evidence, dict) else str(f.evidence or ""),
                "forensic_finding": f.finding or "",
                "why_it_matters": f.why_it_matters or "",
                "recommended_investigation": f.audit_procedure or "",
                "question_for_management": f.management_question or "",
                "evidence_state": f.evidence_state,
            })

        confidence_rec = (
            assessment.confidence[0] if assessment.confidence else None
        )

        snapshot = {
            "assessment_id": assessment.id,
            "analysis_id": assessment.analysis_id,
            "efs_version": assessment.efs_version,
            "status": assessment.assessment_status,
            "overall": {
                "score": assessment.overall_score,
                "score_status": assessment.score_status,
                "risk_level": assessment.risk_level,
                "confidence": assessment.confidence_score or 0.0,
            },
            "pillars": pillars,
            "established_models": {
                "beneish_m_score": established_models.get("beneish_m_score", {}),
                "sloan_accrual": established_models.get("sloan_accrual", {}),
                "altman_z_score": established_models.get("altman_z_score", {}),
                "piotroski_f_score": established_models.get("piotroski_f_score", {}),
                "ohlson_o_score": established_models.get("ohlson_o_score", {}),
            },
            "forensic_findings": findings,
            "red_flags": [rf.finding for rf in assessment.red_flags],
            "management_questions": [mq.question for mq in assessment.management_questions],
            "limitations": confidence_rec.limitations if confidence_rec and confidence_rec.limitations else [],
            "audit_trail": {
                "assessment_id": assessment.id,
                "analysis_id": assessment.analysis_id,
                "efs_version": assessment.efs_version,
                "scoring_version": assessment.scoring_version,
                "rulebook_version": assessment.rulebook_version,
                "engine_version": assessment.engine_version,
                "timestamp": assessment.completed_at.isoformat() if assessment.completed_at else assessment.created_at.isoformat(),
                "variables_evaluated": assessment.variables_evaluated or 0,
                "variables_available": len([v for v in assessment.variables if v.status == "AVAILABLE"]),
                "rules_evaluated": len(assessment.findings),
                "rules_triggered": assessment.rules_triggered or 0,
                "calculation_time_ms": 0.0,  # Original time not re-stored in snapshot
            },
            "input_snapshot_hash": assessment.input_snapshot_hash,
            "assessment_snapshot_hash": assessment.assessment_snapshot_hash,
            "_persisted": True,
        }
        return snapshot


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _confidence_level(score: float) -> str:
    if score >= 75:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def _build_result_dict_for_hashing(result: Any) -> Dict[str, Any]:
    """Build a minimal canonical dict of EFSExecutionResult for SHA-256 hashing."""
    pillars_data = []
    for p in result.pillars:
        pillars_data.append({
            "pillar_id": p.pillar_id,
            "pillar_score": p.pillar_score,
            "variables_evaluated": p.variables_evaluated,
            "variables_available": p.variables_available,
            "variables": [
                {
                    "variable_id": v.variable_id,
                    "raw_value": v.raw_value,
                    "score": v.score,
                    "data_status": v.data_status,
                }
                for v in p.variables
            ],
        })

    return {
        "analysis_id": result.analysis_id,
        "efs_version": result.efs_version,
        "overall": {
            "score": result.overall.score,
            "score_status": result.overall.score_status,
            "risk_level": result.overall.risk_level,
            "confidence": result.overall.confidence,
        },
        "pillars": pillars_data,
        "established_models": {
            k: v if isinstance(v, dict) else _safe_dict(v)
            for k, v in result.established_models.items()
        },
        "rules_triggered": sum(1 for f in result.forensic_findings if f.triggered),
        "rules_evaluated": len(result.forensic_findings),
        "audit_trail": {
            "assessment_id": result.audit_trail.assessment_id,
            "efs_version": result.audit_trail.efs_version,
            "rulebook_version": result.audit_trail.rulebook_version,
            "scoring_version": result.audit_trail.scoring_version,
        },
    }
