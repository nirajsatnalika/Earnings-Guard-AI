"""Schemas for Phase 6A Data Ingestion & Human Review workflow."""

from pydantic import BaseModel, ConfigDict, Field


class CanonicalExtractedItem(BaseModel):
    """A canonical financial item or evidence record extracted from a document with full provenance metadata."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Unique item identifier within the analysis.")
    raw_label: str = Field(description="Original line item label from document.")
    raw_value: str = Field(description="Original unparsed string value.")
    normalized_value: float | None = Field(description="Normalized numeric value, or None if unparseable/missing.")
    unit: str | None = Field(description="Detected unit scale (e.g. thousands, millions, crores), or None.")
    currency: str | None = Field(description="Detected currency code (e.g. INR, USD, EUR), or None.")
    period: str | None = Field(description="Extracted financial period (e.g. FY 2025, Current Year), or None.")
    periods: dict[str, float] | None = Field(default=None, description="Multi-year period dictionary (e.g. {'FY2025': 125000, 'FY2024': 118000}).")
    evidence_category: str | None = Field(default="FINANCIAL_STATEMENT", description="FINANCIAL_STATEMENT, NOTE_DISCLOSURE, or GOVERNANCE_AUDITOR.")
    evidence_text: str | None = Field(default=None, description="Raw text snippet or footnote evidence string.")
    source_filename: str = Field(description="Filename of the uploaded document.")
    source_page: int | None = Field(default=None, description="Page number for PDF documents.")
    source_sheet: str | None = Field(default=None, description="Sheet name for Excel/CSV documents.")
    source_section: str | None = Field(default=None, description="Report section (e.g. Balance Sheet, Notes, Auditor Report).")
    canonical_field: str | None = Field(description="Mapped canonical field name, or None.")
    mapped_efs_variable: str | None = Field(description="Primary mapped EFS variable ID (e.g. FSQ01), or None.")
    raw_variable_key: str | None = Field(description="Input raw_variable dictionary key (e.g. revenue), or None.")
    mapping_status: str = Field(description="EXACT_MATCH, HIGH_CONFIDENCE_MATCH, REVIEW_REQUIRED, or UNMAPPED.")
    confidence: int = Field(ge=0, le=100, description="Confidence score 0 to 100.")
    review_status: str = Field(default="PENDING", description="PENDING, ACCEPTED, EDITED, or REJECTED.")
    notes: str | None = Field(default=None, description="Normalization or extraction warnings.")


class IngestResponse(BaseModel):
    """Response returned after extracting, normalizing, and mapping uploaded documents."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str
    is_scanned_pdf: bool = Field(default=False)
    scanned_pdf_message: str | None = Field(default=None)
    extracted_items: list[CanonicalExtractedItem] = Field(default_factory=list)


class ReviewActionItem(BaseModel):
    """Single human review decision (accept, edit, reject, or remap)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    action: str = Field(description="accept, edit, reject, or remap")
    edited_value: float | None = Field(default=None, description="Override numeric value if action is edit.")
    remapped_canonical_field: str | None = Field(default=None, description="New canonical field if action is remap.")


class ConfirmReviewRequest(BaseModel):
    """Request payload confirming human review actions for an analysis."""

    model_config = ConfigDict(extra="forbid")

    items: list[CanonicalExtractedItem]


class ConfirmReviewResponse(BaseModel):
    """Response containing final confirmed raw_variables payload ready for EFSEngine."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    confirmed_raw_variables: dict[str, float]
