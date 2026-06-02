"""Logging module for application errors"""
import logging
from pathlib import Path


class LogManager:
    """Manages application logging"""

    def __init__(self, logs_dir):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

        # Configure error logging
        self.error_logger = logging.getLogger('error_logger')
        self.error_logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler(self.logs_dir / 'error.log')
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.error_logger.addHandler(error_handler)

    def log_error(self, message):
        """Log error message to error.log"""
        self.error_logger.error(message)
