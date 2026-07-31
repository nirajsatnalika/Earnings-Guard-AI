"""Centralized application logging configuration."""

import logging

from app.core.config import settings


def configure_logging() -> None:
	"""Configure consistent logs for local and hosted runs."""
	logging.basicConfig(
		level=logging.DEBUG if settings.debug else logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		force=True,
	)
