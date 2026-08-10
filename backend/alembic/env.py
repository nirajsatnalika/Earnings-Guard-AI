"""Alembic environment configuration for EarningsGuard™ AI.

DATABASE_URL is loaded exclusively from environment variables / .env file.
It is never hardcoded here or in alembic.ini.
"""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# ─── Path setup ───────────────────────────────────────────────────────────────
# Add backend/ to sys.path so that app imports resolve correctly
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

# Load .env from backend/ directory
load_dotenv(backend_dir / ".env")

# ─── Alembic Config ───────────────────────────────────────────────────────────
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ─── Load DATABASE_URL from environment ───────────────────────────────────────
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Set it in backend/.env (never commit credentials).\n"
        "Example: DATABASE_URL=postgresql+psycopg://user:pass@host.neon.tech/dbname?sslmode=require"
    )

# Alembic requires the URL in the configuration
config.set_main_option("sqlalchemy.url", database_url)

# ─── Import all models so Alembic sees the full metadata ──────────────────────
from app.database.database import Base  # noqa: E402
import app.models  # noqa: E402, F401  — triggers all model imports

target_metadata = Base.metadata


# ─── Migration runners ────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — SQL only, no live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
