"""Logging configuration for AWS Network Tools."""

import logging
import sys
from typing import Optional

# Module logger
logger = logging.getLogger("aws_network_tools")


def setup_logging(
    debug: bool = False, log_file: Optional[str] = None
) -> logging.Logger:
    """Configure logging for the application.

    Args:
        debug: Enable debug level logging
        log_file: Optional file path for log output

    Returns:
        Configured logger instance
    """
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler (only warnings+ unless debug)
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.DEBUG if debug else logging.WARNING)
    console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger for a module.

    Args:
        name: Module name (e.g., 'cloudwan', 'vpc')

    Returns:
        Child logger instance
    """
    return logger.getChild(name)
