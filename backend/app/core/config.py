"""Application configuration using pydantic-settings for environment variable management."""

import os
from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        """Central application settings loaded from environment variables and .env file."""

        model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

        PROJECT_NAME: str = "EarningsGuard AI"
        API_V1_PREFIX: str = "/api/v1"
        UPLOAD_DIR: Path = Path("uploads")

        # Database — loaded from environment only, never hardcoded
        DATABASE_URL: str = Field(
            default="sqlite:///./earningsguard_dev.db",
            description="PostgreSQL or SQLite connection string. Set in backend/.env.",
        )

        # AI Provider configuration
        AI_PROVIDER: str = Field(default="fallback", description="AI provider: openai, gemini, or fallback.")
        OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key.")
        GEMINI_API_KEY: Optional[str] = Field(default=None, description="Gemini API key.")

        # CORS
        CORS_ORIGINS: str = Field(
            default="http://localhost:5173,http://localhost:3000",
            description="Comma-separated allowed CORS origins.",
        )

        def ensure_upload_dir(self) -> None:
            self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        @property
        def cors_origins_list(self) -> list[str]:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

except ImportError:
    # Graceful fallback if pydantic-settings not installed yet
    class Settings:  # type: ignore[no-redef]
        """Fallback plain settings class used before pydantic-settings is installed."""

        PROJECT_NAME: str = "EarningsGuard AI"
        API_V1_PREFIX: str = "/api/v1"
        UPLOAD_DIR: Path = Path("uploads")
        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./earningsguard_dev.db")
        AI_PROVIDER: str = os.getenv("AI_PROVIDER", "fallback")
        OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
        CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")

        def ensure_upload_dir(self) -> None:
            self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        @property
        def cors_origins_list(self) -> list[str]:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

        @property
        def database_url(self) -> str:
            return self.DATABASE_URL


settings = Settings()
