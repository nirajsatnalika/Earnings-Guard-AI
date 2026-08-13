"""Parser service — orchestrates reading uploaded statements into DataFrames.

Parsed DataFrames are held in an in-memory store keyed by analysis_id. No
database is used, and no field mapping, validation, ratios, Beneish, or EFS
calculations are performed — this is purely the parsing stage.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.config import settings
from app.core.exceptions import (
    AnalysisNotFoundError,
    FileParsingError,
    NoFilesFoundError,
    UnsupportedFileFormatError,
)
from app.core.logging import get_logger
from app.schemas.parse import ParseResponse, ParsedSheet, ParsedStatement
from app.services.pdf_extraction_service import PDFExtractionResult, parse_pdf
from app.utils.csv_util import parse_csv
from app.utils.excel_util import parse_excel

logger = get_logger(__name__)

# Maps the upload field-name prefix used on disk back to a human statement label.
_STATEMENT_LABELS: dict[str, str] = {
    "balance_sheet": "Balance Sheet",
    "profit_loss": "Profit & Loss Statement",
    "cash_flow": "Cash Flow Statement",
    "annual_report": "Annual Report",
}

# In-memory store: analysis_id -> { statement_label: { sheet_name: DataFrame } }
_parsed_store: dict[str, dict[str, dict[str, pd.DataFrame]]] = {}

# Provenance store: analysis_id -> list of raw extraction provenance records
_provenance_store: dict[str, list[dict[str, Any]]] = {}
# PDF status store: analysis_id -> dict of PDF status metadata
_pdf_status_store: dict[str, list[dict[str, Any]]] = {}


def _statement_label_for(filename: str) -> str:
    """Resolve the human statement label from a stored file's prefix."""
    stem = Path(filename).stem.lower()
    for prefix, label in _STATEMENT_LABELS.items():
        if stem.startswith(prefix):
            return label
    # Fall back to the file stem if the naming convention ever changes.
    return Path(filename).stem


def _dispatch(path: Path) -> tuple[dict[str, pd.DataFrame], PDFExtractionResult | None]:
    """Route a single file to the correct utility based on its extension."""
    ext = path.suffix.lower()
    if ext in (".xlsx", ".xls"):
        return parse_excel(str(path)), None
    if ext == ".csv":
        return parse_csv(str(path)), None
    if ext == ".pdf":
        res = parse_pdf(str(path))
        return res.frames, res
    raise UnsupportedFileFormatError(path.name)


from typing import Any, Dict, List, Optional, Tuple


class ParserService:
    """Parses all uploaded statements for an analysis into DataFrames."""

    @staticmethod
    def parse(analysis_id: str) -> ParseResponse:
        upload_dir = settings.UPLOAD_DIR / analysis_id
        if not upload_dir.exists() or not upload_dir.is_dir():
            logger.warning("Parse requested for unknown analysis %s", analysis_id)
            raise AnalysisNotFoundError(analysis_id)

        files = sorted(p for p in upload_dir.iterdir() if p.is_file())
        if not files:
            raise NoFilesFoundError(analysis_id)

        parsed_statements: list[ParsedStatement] = []
        in_memory: dict[str, dict[str, pd.DataFrame]] = {}
        prov_list: list[dict[str, Any]] = []
        pdf_statuses: list[dict[str, Any]] = []

        for file_path in files:
            statement_label = _statement_label_for(file_path.name)
            logger.info("Parsing %s (%s) for analysis %s", file_path.name, statement_label, analysis_id)

            sheets, pdf_res = _dispatch(file_path)

            if pdf_res is not None:
                pdf_statuses.append({
                    "filename": pdf_res.filename,
                    "is_scanned": pdf_res.is_scanned,
                    "message": pdf_res.message,
                })
                if pdf_res.provenance:
                    prov_list.extend(pdf_res.provenance)

            sheet_summaries: list[ParsedSheet] = []
            statement_frames: dict[str, pd.DataFrame] = {}

            for sheet_name, frame in sheets.items():
                sheet_summaries.append(
                    ParsedSheet(
                        name=sheet_name,
                        rows=int(frame.shape[0]),
                        columns=int(frame.shape[1]),
                    )
                )
                statement_frames[sheet_name] = frame

            parsed_statements.append(
                ParsedStatement(
                    statement=statement_label,
                    filename=file_path.name,
                    sheets=sheet_summaries,
                )
            )
            in_memory[statement_label] = statement_frames

        _parsed_store[analysis_id] = in_memory
        _provenance_store[analysis_id] = prov_list
        _pdf_status_store[analysis_id] = pdf_statuses

        logger.info(
            "Analysis %s: parsed %d statement(s), held in memory",
            analysis_id,
            len(parsed_statements),
        )
        return ParseResponse(
            analysis_id=analysis_id,
            status="parsed",
            statements=parsed_statements,
        )

    @staticmethod
    def get_frames(analysis_id: str) -> dict[str, dict[str, pd.DataFrame]] | None:
        """Access the in-memory parsed DataFrames for an analysis, if present."""
        return _parsed_store.get(analysis_id)

    @staticmethod
    def get_provenance(analysis_id: str) -> list[dict[str, Any]]:
        """Access the extracted PDF/Excel provenance records for an analysis."""
        return _provenance_store.get(analysis_id, [])

    @staticmethod
    def get_pdf_status(analysis_id: str) -> list[dict[str, Any]]:
        """Access PDF status metadata (e.g. scanned PDF warning) for an analysis."""
        return _pdf_status_store.get(analysis_id, [])
