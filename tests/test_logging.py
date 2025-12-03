"""Tests for logging configuration."""

import logging
import tempfile
import os

from aws_network_tools.core.logging import setup_logging, get_logger, logger


class TestLogging:
    """Tests for logging configuration."""

    def test_logger_exists(self):
        """Module logger should exist."""
        assert logger is not None
        assert logger.name == "aws_network_tools"

    def test_setup_logging_default(self):
        """setup_logging should configure logger with defaults."""
        result = setup_logging()
        assert result is logger
        assert result.level == logging.INFO

    def test_setup_logging_debug(self):
        """setup_logging with debug=True should set DEBUG level."""
        result = setup_logging(debug=True)
        assert result.level == logging.DEBUG

    def test_setup_logging_with_file(self):
        """setup_logging with log_file should add file handler."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            log_file = f.name
        try:
            result = setup_logging(debug=True, log_file=log_file)
            result.info("Test message")
            # Check file was written
            with open(log_file) as f:
                content = f.read()
            assert "Test message" in content
        finally:
            os.unlink(log_file)

    def test_get_logger(self):
        """get_logger should return child logger."""
        child = get_logger("cloudwan")
        assert child.name == "aws_network_tools.cloudwan"
        assert child.parent is logger

    def test_get_logger_different_modules(self):
        """get_logger should return different loggers for different modules."""
        cloudwan = get_logger("cloudwan")
        vpc = get_logger("vpc")
        assert cloudwan is not vpc
        assert cloudwan.name != vpc.name
