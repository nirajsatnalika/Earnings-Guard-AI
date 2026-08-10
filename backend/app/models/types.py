"""Portable JSON column type — JSONB on PostgreSQL, JSON on SQLite.

Import _JsonColumn instead of JSONB or JSON directly in all ORM model files.
This ensures tests against SQLite in-memory databases work correctly while
production Neon PostgreSQL uses the full JSONB type.
"""

from sqlalchemy import JSON
from sqlalchemy.types import TypeDecorator, Text


class _JsonColumn(TypeDecorator):
    """SQLAlchemy TypeDecorator that uses JSONB on PostgreSQL and JSON elsewhere."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from sqlalchemy.dialects.postgresql import JSONB
                return dialect.type_descriptor(JSONB())
            except ImportError:
                pass
        return dialect.type_descriptor(JSON())
