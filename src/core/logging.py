"""
Logging configuration and utilities.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from config.settings import LoggingSettings


def setup_logging(
    level: int = logging.INFO,
    settings: Optional[LoggingSettings] = None,
    name: str = "chimera"
) -> logging.Logger:
    """
    Setup structured logging for the application.

    Args:
        level: Logging level
        settings: Logging configuration settings
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if settings:
        formatter = logging.Formatter(
            settings.format,
            datefmt=settings.date_format
        )
    else:
        formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if settings and settings.file_enabled:
        # Ensure log directory exists
        log_path = Path(settings.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            settings.file_path,
            maxBytes=settings.file_max_bytes,
            backupCount=settings.file_backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(f"chimera.{name}")


# Global logger instance
logger = get_logger(__name__)