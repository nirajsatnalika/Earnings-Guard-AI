"""SQLAlchemy ORM model: assessment_audit_log table."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import _JsonColumn

from app.database.database import Base


class AssessmentAuditLog(Base):
    """Immutable audit log capturing key lifecycle events for an assessment."""

    __tablename__ = "assessment_audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), sa.ForeignKey("assessments.id"), nullable=False, index=True)
    execution_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    # Event types: ASSESSMENT_CREATED, ENGINE_STARTED, ENGINE_COMPLETED, ENGINE_FAILED,
    #              NARRATIVE_GENERATED, NARRATIVE_FALLBACK, NARRATIVE_FAILED,
    #              REPORT_RETRIEVED, SNAPSHOT_PERSISTED
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_data: Mapped[dict] = mapped_column(_JsonColumn, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="audit_log")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AssessmentAuditLog event_type={self.event_type} assessment_id={self.assessment_id}>"
