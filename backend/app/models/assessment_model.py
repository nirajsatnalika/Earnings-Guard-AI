"""SQLAlchemy ORM model: assessment_models table.

Stores results for the 5 established academic forensic/credit models separately.
Models: Beneish M-Score, Sloan Accrual, Altman Z-Score, Piotroski F-Score, Ohlson O-Score.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import String, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import _JsonColumn

from app.database.database import Base


class AssessmentModel(Base):
    """Stores one established model result per row for an assessment."""

    __tablename__ = "assessment_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), sa.ForeignKey("assessments.id"), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_role: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    # Full model result dict (score, status, interpretation, etc.)
    result: Mapped[dict] = mapped_column(_JsonColumn, nullable=False, default=dict)
    signal: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    interpretation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    components: Mapped[dict] = mapped_column(_JsonColumn, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="models")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AssessmentModel {self.model_name}>"
