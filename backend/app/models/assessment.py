"""SQLAlchemy ORM model: assessments table.

Each completed assessment is an immutable forensic snapshot.
Includes input_snapshot_hash and assessment_snapshot_hash for audit integrity.

CRITICAL: overall_score and risk_level are NULL when calibration is pending.
DO NOT store fabricated values.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import String, Float, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Assessment(Base):
    """Immutable EFS™ assessment snapshot stored in PostgreSQL."""

    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "assessment_status IN ('DRAFT', 'RUNNING', 'COMPLETED', 'FAILED')",
            name="ck_assessment_status",
        ),
        CheckConstraint(
            "score_status IN ('CALIBRATION_PENDING', 'COMPLETED')",
            name="ck_score_status",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        String(36), sa.ForeignKey("companies.id"), nullable=False, index=True
    )
    # The external analysis_id used to call the EFS engine
    analysis_id: Mapped[str] = mapped_column(
        String(256), nullable=False, unique=True, index=True
    )
    assessment_status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")

    # Methodology version metadata
    efs_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")
    methodology_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")
    scoring_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")
    rulebook_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")
    engine_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")

    # EFS Score — NULL when CALIBRATION_PENDING
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    score_status: Mapped[str] = mapped_column(String(32), nullable=False, default="CALIBRATION_PENDING")

    # Confidence
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_level: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    # Audit counters
    rules_triggered: Mapped[Optional[int]] = mapped_column(nullable=True)
    variables_evaluated: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Snapshot integrity hashes (SHA-256 hex, deterministic canonical serialization)
    # Generated server-side. Audit/integrity metadata ONLY — do not alter scoring.
    input_snapshot_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    assessment_snapshot_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="assessments")  # noqa: F821
    inputs: Mapped[list["AssessmentInput"]] = relationship(  # noqa: F821
        "AssessmentInput", back_populates="assessment", cascade="all, delete-orphan"
    )
    variables: Mapped[list["AssessmentVariable"]] = relationship(  # noqa: F821
        "AssessmentVariable", back_populates="assessment", cascade="all, delete-orphan"
    )
    pillars: Mapped[list["AssessmentPillar"]] = relationship(  # noqa: F821
        "AssessmentPillar", back_populates="assessment", cascade="all, delete-orphan"
    )
    models: Mapped[list["AssessmentModel"]] = relationship(  # noqa: F821
        "AssessmentModel", back_populates="assessment", cascade="all, delete-orphan"
    )
    findings: Mapped[list["AssessmentFinding"]] = relationship(  # noqa: F821
        "AssessmentFinding", back_populates="assessment", cascade="all, delete-orphan"
    )
    red_flags: Mapped[list["AssessmentRedFlag"]] = relationship(  # noqa: F821
        "AssessmentRedFlag", back_populates="assessment", cascade="all, delete-orphan"
    )
    management_questions: Mapped[list["AssessmentManagementQuestion"]] = relationship(  # noqa: F821
        "AssessmentManagementQuestion", back_populates="assessment", cascade="all, delete-orphan"
    )
    confidence: Mapped[list["AssessmentConfidence"]] = relationship(  # noqa: F821
        "AssessmentConfidence", back_populates="assessment", cascade="all, delete-orphan"
    )
    narratives: Mapped[list["AssessmentNarrative"]] = relationship(  # noqa: F821
        "AssessmentNarrative", back_populates="assessment", cascade="all, delete-orphan"
    )
    audit_log: Mapped[list["AssessmentAuditLog"]] = relationship(  # noqa: F821
        "AssessmentAuditLog", back_populates="assessment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Assessment id={self.id} analysis_id={self.analysis_id!r} status={self.assessment_status}>"
