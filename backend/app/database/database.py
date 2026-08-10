"""SQLAlchemy engine, session factory, and declarative base.

DATABASE_URL is loaded exclusively from environment / .env file via Settings.
It is never hardcoded or logged.
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from app.core.config import settings


class Base(DeclarativeBase):
    """Shared declarative base for all EarningsGuard ORM models."""


def _build_engine(database_url: str) -> Any:
    """Build a SQLAlchemy engine with settings appropriate for the database driver."""
    url = database_url.strip()

    if url.startswith("sqlite"):
        # SQLite: used for local dev / test only
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            pool_pre_ping=True,
        )
    else:
        # PostgreSQL (Neon via psycopg3 / psycopg2)
        # NullPool is recommended for serverless Neon connections
        return create_engine(
            url,
            poolclass=NullPool,
            pool_pre_ping=True,
        )


# Database URL property access — handles both pydantic-settings and fallback plain class
_db_url: str = getattr(settings, "DATABASE_URL", None) or getattr(settings, "database_url", "sqlite:///./earningsguard_dev.db")

engine = _build_engine(_db_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def init_db() -> None:
    """Create all tables from metadata. Used for SQLite testing only.

    In production with Neon PostgreSQL, use: alembic upgrade head
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a managed SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Generator[Session, None, None]:
    """Yield a managed SQLAlchemy session for non-request callers (backward compat)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
