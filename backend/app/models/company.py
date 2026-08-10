"""SQLAlchemy ORM model: companies table."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Company(Base):
    """Represents a company entity tracked by EarningsGuard™ AI."""

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    legal_name: Mapped[str] = mapped_column(String(512), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ticker: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    exchange: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    assessments: Mapped[list["Assessment"]] = relationship(  # noqa: F821
        "Assessment", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} legal_name={self.legal_name!r}>"
