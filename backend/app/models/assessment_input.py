"""SQLAlchemy ORM model: assessment_inputs table."""

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import String, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import _JsonColumn

from app.database.database import Base


class AssessmentInput(Base):
    """Stores the raw input payload submitted for an EFS assessment."""

    __tablename__ = "assessment_inputs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), sa.ForeignKey("assessments.id"), nullable=False, index=True)
    input_payload: Mapped[dict] = mapped_column(_JsonColumn, nullable=False, default=dict)
    source_metadata: Mapped[dict] = mapped_column(_JsonColumn, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="inputs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AssessmentInput id={self.id} assessment_id={self.assessment_id}>"
