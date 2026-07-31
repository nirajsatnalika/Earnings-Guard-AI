"""Secure local storage service for financial statement uploads."""

from collections.abc import Iterable
import logging
from pathlib import Path
from typing import BinaryIO
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.schemas.upload import UploadedFileResponse
from app.utils.upload_validation import (
    CHUNK_SIZE,
    format_size,
    sanitize_filename,
    validate_extension,
    validate_size,
)

logger = logging.getLogger(__name__)


class UploadValidationError(ValueError):
    """Raised when an uploaded statement does not meet storage requirements."""


class UploadService:
    """Validate and persist uploaded statement files without parsing their contents."""

    def __init__(self, upload_root: Path) -> None:
        self.upload_root = upload_root

    def save_statement_files(
        self,
        analysis_id: UUID,
        files: Iterable[tuple[str, UploadFile]],
    ) -> list[UploadedFileResponse]:
        """Store all files for one analysis and return their public metadata."""
        analysis_directory = self.upload_root / str(analysis_id)
        analysis_directory.mkdir(parents=True, exist_ok=True)
        saved_paths: list[Path] = []
        metadata: list[UploadedFileResponse] = []

        try:
            for statement_type, upload in files:
                saved_path, file_metadata = self._save_one(
                    analysis_directory=analysis_directory,
                    statement_type=statement_type,
                    upload=upload,
                )
                saved_paths.append(saved_path)
                metadata.append(file_metadata)
        except Exception:
            for saved_path in saved_paths:
                saved_path.unlink(missing_ok=True)
            analysis_directory.rmdir()
            raise

        return metadata

    def _save_one(
        self,
        analysis_directory: Path,
        statement_type: str,
        upload: UploadFile,
    ) -> tuple[Path, UploadedFileResponse]:
        original_name = sanitize_filename(upload.filename)
        try:
            extension = validate_extension(original_name, statement_type)
        except ValueError as exc:
            raise UploadValidationError(str(exc)) from exc

        destination = analysis_directory / f"{uuid4()}_{original_name}"
        size_bytes = self._write_with_limit(upload.file, destination)
        logger.info("Stored %s upload as %s (%d bytes)", statement_type, destination.name, size_bytes)
        return destination, UploadedFileResponse(
            statement=statement_type,
            filename=original_name,
            size=format_size(size_bytes),
            extension=extension,
        )

    @staticmethod
    def _write_with_limit(source: BinaryIO, destination: Path) -> int:
        total_size = 0
        try:
            with destination.open("wb") as target:
                while chunk := source.read(CHUNK_SIZE):
                    total_size += len(chunk)
                    try:
                        validate_size(total_size)
                    except ValueError as exc:
                        raise UploadValidationError(str(exc)) from exc
                    target.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return total_size

