"""SQLAlchemy ORM model: assessment_confidence table."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import _JsonColumn

from app.database.database import Base


class AssessmentConfidence(Base):
    """Stores multi-factor confidence evaluation result for an assessment."""

    __tablename__ = "assessment_confidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), sa.ForeignKey("assessments.id"), nullable=False, unique=True, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="Low")
    factors: Mapped[dict] = mapped_column(_JsonColumn, nullable=True, default=dict)
    limitations: Mapped[list] = mapped_column(_JsonColumn, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="confidence")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AssessmentConfidence score={self.confidence_score} level={self.confidence_level}>"
