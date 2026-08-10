"""Initial schema — all 12 EarningsGuard™ AI tables.

Revision ID: 0001
Revises:
Create Date: 2026-08-10

Creates:
- companies
- assessments
- assessment_inputs
- assessment_variables
- assessment_pillars
- assessment_models
- assessment_findings
- assessment_red_flags
- assessment_management_questions
- assessment_confidence
- assessment_narratives
- assessment_audit_log
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _jsonb_or_json() -> sa.types.TypeEngine:
    """Return JSONB for PostgreSQL, JSON for SQLite (testing)."""
    from sqlalchemy.dialects import postgresql
    try:
        return postgresql.JSONB()
    except Exception:
        return sa.JSON()


def upgrade() -> None:
    # ── companies ─────────────────────────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("legal_name", sa.String(512), nullable=False),
        sa.Column("display_name", sa.String(512), nullable=True),
        sa.Column("ticker", sa.String(32), nullable=True),
        sa.Column("exchange", sa.String(64), nullable=True),
        sa.Column("country", sa.String(128), nullable=True),
        sa.Column("industry", sa.String(256), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_companies_ticker", "companies", ["ticker"])

    # ── assessments ───────────────────────────────────────────────────────────
    op.create_table(
        "assessments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("analysis_id", sa.String(256), nullable=False, unique=True),
        sa.Column("assessment_status", sa.String(32), nullable=False, server_default="DRAFT"),
        sa.Column("efs_version", sa.String(32), nullable=False, server_default="1.0"),
        sa.Column("methodology_version", sa.String(32), nullable=False, server_default="1.0"),
        sa.Column("scoring_version", sa.String(32), nullable=False, server_default="1.0"),
        sa.Column("rulebook_version", sa.String(32), nullable=False, server_default="1.0"),
        sa.Column("engine_version", sa.String(32), nullable=False, server_default="1.0.0"),
        sa.Column("overall_score", sa.Float, nullable=True),
        sa.Column("risk_level", sa.String(64), nullable=True),
        sa.Column("score_status", sa.String(32), nullable=False, server_default="CALIBRATION_PENDING"),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("confidence_level", sa.String(32), nullable=True),
        sa.Column("rules_triggered", sa.Integer, nullable=True),
        sa.Column("variables_evaluated", sa.Integer, nullable=True),
        sa.Column("input_snapshot_hash", sa.String(64), nullable=True),
        sa.Column("assessment_snapshot_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "assessment_status IN ('DRAFT', 'RUNNING', 'COMPLETED', 'FAILED')",
            name="ck_assessment_status",
        ),
        sa.CheckConstraint(
            "score_status IN ('CALIBRATION_PENDING', 'COMPLETED')",
            name="ck_score_status",
        ),
    )
    op.create_index("ix_assessments_analysis_id", "assessments", ["analysis_id"])
    op.create_index("ix_assessments_company_id", "assessments", ["company_id"])

    # ── assessment_inputs ─────────────────────────────────────────────────────
    op.create_table(
        "assessment_inputs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("input_payload", sa.JSON, nullable=False),
        sa.Column("source_metadata", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessment_inputs_assessment_id", "assessment_inputs", ["assessment_id"])

    # ── assessment_variables ──────────────────────────────────────────────────
    op.create_table(
        "assessment_variables",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("variable_id", sa.String(64), nullable=False),
        sa.Column("variable_name", sa.String(256), nullable=False),
        sa.Column("pillar", sa.String(128), nullable=False),
        sa.Column("raw_value", sa.Float, nullable=True),
        sa.Column("score", sa.Integer, nullable=True),
        sa.Column("scoring_band", sa.String(32), nullable=True),
        sa.Column("unit", sa.String(64), nullable=True),
        sa.Column("status", sa.String(64), nullable=False, server_default="AVAILABLE"),
        sa.Column("evidence_state", sa.String(64), nullable=False, server_default="CALCULATED"),
        sa.Column("source_fields", sa.JSON, nullable=True),
        sa.Column("calculation_source", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessment_variables_assessment_id", "assessment_variables", ["assessment_id"])

    # ── assessment_pillars ────────────────────────────────────────────────────
    op.create_table(
        "assessment_pillars",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("pillar_id", sa.String(32), nullable=False),
        sa.Column("pillar_name", sa.String(256), nullable=False),
        sa.Column("pillar_score", sa.Float, nullable=True),
        sa.Column("status", sa.String(64), nullable=False, server_default="COMPLETED"),
        sa.Column("variables_evaluated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("variables_available", sa.Integer, nullable=False, server_default="0"),
        sa.Column("positive_drivers", sa.JSON, nullable=True),
        sa.Column("negative_drivers", sa.JSON, nullable=True),
        sa.Column("data_quality", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessment_pillars_assessment_id", "assessment_pillars", ["assessment_id"])

    # ── assessment_models ─────────────────────────────────────────────────────
    op.create_table(
        "assessment_models",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("model_role", sa.String(128), nullable=True),
        sa.Column("result", sa.JSON, nullable=False),
        sa.Column("signal", sa.String(128), nullable=True),
        sa.Column("interpretation", sa.Text, nullable=True),
        sa.Column("components", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessment_models_assessment_id", "assessment_models", ["assessment_id"])

    # ── assessment_findings ───────────────────────────────────────────────────
    op.create_table(
        "assessment_findings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("rule_id", sa.String(64), nullable=False),
        sa.Column("rule_name", sa.String(256), nullable=False),
        sa.Column("pillar", sa.String(128), nullable=True),
        sa.Column("severity", sa.String(32), nullable=False, server_default="Medium"),
        sa.Column("triggered", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("trigger_condition", sa.Text, nullable=True),
        sa.Column("finding", sa.Text, nullable=True),
        sa.Column("why_it_matters", sa.Text, nullable=True),
        sa.Column("evidence", sa.JSON, nullable=True),
        sa.Column("audit_procedure", sa.Text, nullable=True),
        sa.Column("management_question", sa.Text, nullable=True),
        sa.Column("evidence_state", sa.String(64), nullable=False, server_default="Triggered"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessment_findings_assessment_id", "assessment_findings", ["assessment_id"])

    # ── assessment_red_flags ──────────────────────────────────────────────────
    op.create_table(
        "assessment_red_flags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("rule_id", sa.String(64), nullable=True),
        sa.Column("severity", sa.String(32), nullable=False, server_default="High"),
        sa.Column("finding", sa.Text, nullable=False),
        sa.Column("pillar", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessment_red_flags_assessment_id", "assessment_red_flags", ["assessment_id"])

    # ── assessment_management_questions ───────────────────────────────────────
    op.create_table(
        "assessment_management_questions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("pillar", sa.String(128), nullable=True),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("priority", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessment_management_questions_assessment_id", "assessment_management_questions", ["assessment_id"])

    # ── assessment_confidence ─────────────────────────────────────────────────
    op.create_table(
        "assessment_confidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False, unique=True),
        sa.Column("confidence_score", sa.Float, nullable=False),
        sa.Column("confidence_level", sa.String(32), nullable=False, server_default="Low"),
        sa.Column("factors", sa.JSON, nullable=True),
        sa.Column("limitations", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessment_confidence_assessment_id", "assessment_confidence", ["assessment_id"])

    # ── assessment_narratives ─────────────────────────────────────────────────
    op.create_table(
        "assessment_narratives",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("narrative_version", sa.String(16), nullable=False, server_default="1.0"),
        sa.Column("provider", sa.String(64), nullable=True),
        sa.Column("model", sa.String(128), nullable=True),
        sa.Column("prompt_version", sa.String(32), nullable=True),
        sa.Column("narrative_payload", sa.JSON, nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="FALLBACK"),
        sa.CheckConstraint(
            "status IN ('COMPLETED', 'FALLBACK', 'UNAVAILABLE')",
            name="ck_narrative_status",
        ),
    )
    op.create_index("ix_assessment_narratives_assessment_id", "assessment_narratives", ["assessment_id"])

    # ── assessment_audit_log ──────────────────────────────────────────────────
    op.create_table(
        "assessment_audit_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assessment_id", sa.String(36), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("execution_id", sa.String(64), nullable=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("event_data", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessment_audit_log_assessment_id", "assessment_audit_log", ["assessment_id"])


def downgrade() -> None:
    op.drop_table("assessment_audit_log")
    op.drop_table("assessment_narratives")
    op.drop_table("assessment_confidence")
    op.drop_table("assessment_management_questions")
    op.drop_table("assessment_red_flags")
    op.drop_table("assessment_findings")
    op.drop_table("assessment_models")
    op.drop_table("assessment_pillars")
    op.drop_table("assessment_variables")
    op.drop_table("assessment_inputs")
    op.drop_table("assessments")
    op.drop_table("companies")
