import logging

from app.core.config import settings


def configure_logging() -> None:
    """Configure root logger with a structured format and env-driven log level."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
