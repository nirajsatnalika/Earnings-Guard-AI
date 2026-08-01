"""Application configuration."""

from pathlib import Path


class Settings:
    """Central application settings.

    Kept as a plain class (no pydantic-settings dependency) to match the
    existing lightweight configuration approach.
    """

    PROJECT_NAME: str = "EarningsGuard AI"
    API_V1_PREFIX: str = "/api/v1"
    UPLOAD_DIR: Path = Path("uploads")

    def ensure_upload_dir(self) -> None:
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
