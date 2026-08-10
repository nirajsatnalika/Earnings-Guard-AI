"""SQLAlchemy ORM model: assessment_findings table."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import String, Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import _JsonColumn

from app.database.database import Base


class AssessmentFinding(Base):
    """Stores evaluated forensic rule findings for an assessment."""

    __tablename__ = "assessment_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), sa.ForeignKey("assessments.id"), nullable=False, index=True)
    rule_id: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(256), nullable=False)
    pillar: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="Medium")
    triggered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    trigger_condition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    finding: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    why_it_matters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict] = mapped_column(_JsonColumn, nullable=True, default=dict)
    audit_procedure: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    management_question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_state: Mapped[str] = mapped_column(String(64), nullable=False, default="Triggered")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="findings")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AssessmentFinding rule_id={self.rule_id} triggered={self.triggered}>"
