"""SQLAlchemy ORM model: assessment_variables table."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import String, Float, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import _JsonColumn

from app.database.database import Base


class AssessmentVariable(Base):
    """Stores evaluated EFS variable evidence for one assessment."""

    __tablename__ = "assessment_variables"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), sa.ForeignKey("assessments.id"), nullable=False, index=True)
    variable_id: Mapped[str] = mapped_column(String(64), nullable=False)
    variable_name: Mapped[str] = mapped_column(String(256), nullable=False)
    pillar: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scoring_band: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    # AVAILABLE, MISSING, NOT_APPLICABLE, INSUFFICIENT_EVIDENCE
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="AVAILABLE")
    # CALCULATED, PROVIDED, DISCLOSURE INPUT, NOT EVALUATED, NOT APPLICABLE, INSUFFICIENT EVIDENCE
    evidence_state: Mapped[str] = mapped_column(String(64), nullable=False, default="CALCULATED")
    source_fields: Mapped[list] = mapped_column(_JsonColumn, nullable=True, default=list)
    calculation_source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="variables")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AssessmentVariable {self.variable_id} score={self.score}>"
