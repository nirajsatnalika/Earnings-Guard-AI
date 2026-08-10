"""SQLAlchemy ORM model: assessment_management_questions table."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import String, Integer, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class AssessmentManagementQuestion(Base):
    """Stores recommended management inquiry questions from triggered forensic rules."""

    __tablename__ = "assessment_management_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), sa.ForeignKey("assessments.id"), nullable=False, index=True)
    pillar: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="management_questions")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AssessmentManagementQuestion pillar={self.pillar}>"
