"""Typed application settings loaded from environment variables."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
	"""Runtime configuration for the EarningsGuard AI service."""

	model_config = ConfigDict(frozen=True, extra="ignore")

	app_name: str = Field(default="EarningsGuard AI", validation_alias="APP_NAME")
	app_version: str = Field(default="1.0.0", validation_alias="APP_VERSION")
	environment: str = Field(default="development", validation_alias="ENVIRONMENT")
	debug: bool = Field(default=False, validation_alias="DEBUG")
	database_url: str = Field(default="sqlite:///./earningsguard.db", validation_alias="DATABASE_URL")
	cors_origins: str = Field(default="http://localhost:5173", validation_alias="CORS_ORIGINS")

	@property
	def cors_origin_list(self) -> list[str]:
		"""Return configured CORS origins as a normalized list."""
		return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
