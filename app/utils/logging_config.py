"""File-based logging configuration for application logs."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parents[2] / "logs" / "app.log"


def configure_logging() -> None:
    """Write application logs to a rotating file without console propagation."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    app_logger.propagate = False

    resolved_log_file = LOG_FILE.resolve()
    if any(
        isinstance(handler, RotatingFileHandler)
        and Path(handler.baseFilename) == resolved_log_file
        for handler in app_logger.handlers
    ):
        return

    file_handler = RotatingFileHandler(
        resolved_log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    app_logger.addHandler(file_handler)
