"""Validation helpers for financial statement uploads."""

from pathlib import Path

MAX_FILE_SIZE = 25 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
ALLOWED_UPLOAD_EXTENSIONS = frozenset({".xlsx", ".xls", ".csv"})


def sanitize_filename(filename: str | None) -> str:
    """Return only the basename supplied by the client."""
    return Path(filename or "").name


def validate_extension(filename: str, statement: str) -> str:
    """Validate and return a normalized supported extension."""
    extension = Path(filename).suffix.lower()
    if not filename or extension not in ALLOWED_UPLOAD_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_UPLOAD_EXTENSIONS))
        raise ValueError(f"{statement} must use one of: {allowed}")
    return extension


def validate_size(size_bytes: int) -> None:
    """Raise when a file exceeds the 25 MB per-file limit."""
    if size_bytes > MAX_FILE_SIZE:
        raise ValueError("Each uploaded file must be 25 MB or smaller")


def format_size(size_bytes: int) -> str:
    """Format a byte count for the upload response."""
    if size_bytes < 1024 * 1024:
        return f"{max(1, round(size_bytes / 1024))} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"
