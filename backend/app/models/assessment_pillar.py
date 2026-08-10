"""SQLAlchemy ORM model: assessment_pillars table."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import String, Float, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import _JsonColumn

from app.database.database import Base


class AssessmentPillar(Base):
    """Stores the aggregated result for each of the 7 EFS pillars."""

    __tablename__ = "assessment_pillars"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), sa.ForeignKey("assessments.id"), nullable=False, index=True)
    pillar_id: Mapped[str] = mapped_column(String(32), nullable=False)
    pillar_name: Mapped[str] = mapped_column(String(256), nullable=False)
    # NULL when calibration pending
    pillar_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="COMPLETED")
    variables_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    variables_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    positive_drivers: Mapped[list] = mapped_column(_JsonColumn, nullable=True, default=list)
    negative_drivers: Mapped[list] = mapped_column(_JsonColumn, nullable=True, default=list)
    data_quality: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="pillars")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AssessmentPillar {self.pillar_id} score={self.pillar_score}>"
