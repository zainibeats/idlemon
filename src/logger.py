"""Logging module for application diagnostics."""
import logging
from pathlib import Path


def _has_file_handler(logger, log_file):
    """Return True when logger already writes to log_file."""
    return any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == log_file
        for handler in logger.handlers
    )


class LogManager:
    """Manages application logging."""

    def __init__(self, logs_dir):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = (self.logs_dir / 'error.log').resolve()

        # Configure application logging.
        self.error_logger = logging.getLogger(f'idlemon.error.{log_file}')
        self.error_logger.setLevel(logging.INFO)
        self.error_logger.propagate = False
        if not _has_file_handler(self.error_logger, log_file):
            error_handler = logging.FileHandler(log_file)
            error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.error_logger.addHandler(error_handler)

    def log_info(self, message):
        """Log informational message to error.log."""
        self.error_logger.info(message)

    def log_warning(self, message):
        """Log warning message to error.log."""
        self.error_logger.warning(message)

    def log_error(self, message):
        """Log error message to error.log."""
        self.error_logger.error(message)
