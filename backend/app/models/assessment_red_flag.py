"""SQLAlchemy ORM model: assessment_red_flags table."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import String, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class AssessmentRedFlag(Base):
    """Stores high-severity forensic red flags triggered in an assessment."""

    __tablename__ = "assessment_red_flags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), sa.ForeignKey("assessments.id"), nullable=False, index=True)
    rule_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="High")
    finding: Mapped[str] = mapped_column(Text, nullable=False)
    pillar: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="red_flags")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AssessmentRedFlag rule_id={self.rule_id} severity={self.severity}>"
