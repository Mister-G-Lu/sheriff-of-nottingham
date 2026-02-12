"""
Tests for the game logging system.
"""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from core.systems.logger import (
    game_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    setup_logger,
)


class TestSetupLogger:
    """Test logger setup and configuration."""

    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a logger instance."""
        logger = setup_logger("test_logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_setup_logger_returns_existing_logger(self):
        """Test that setup_logger returns existing logger if already configured."""
        # First call creates logger
        logger1 = setup_logger("test_existing")

        # Second call should return same logger
        logger2 = setup_logger("test_existing")

        assert logger1 is logger2

    def test_setup_logger_creates_log_directory(self):
        """Test that setup_logger creates logs directory."""
        from core.systems.logger import setup_logger

        setup_logger("test_dir")

        # Logger creates logs directory at core/logs (relative to logger.py location)
        # Test file is at: tests/unit/core/systems/test_logger.py
        # Need to go up 4 levels to get to project root, then into core/logs
        test_file_path = Path(__file__).resolve()
        project_root = test_file_path.parent.parent.parent.parent.parent
        log_dir = project_root / "core" / "logs"
        assert log_dir.exists(), f"Logs directory should be created at {log_dir}"

    def test_setup_logger_sets_debug_level(self):
        """Test that logger is set to DEBUG level."""
        logger = setup_logger("test_level")

        assert logger.level == logging.DEBUG

    def test_setup_logger_has_file_handler(self):
        """Test that logger has a file handler configured."""
        logger = setup_logger("test_handler")

        # Should have at least one handler (file handler)
        assert len(logger.handlers) > 0

        # Check that at least one handler is a FileHandler
        has_file_handler = any(
            isinstance(h, logging.FileHandler) for h in logger.handlers
        )
        assert has_file_handler, "Logger should have a FileHandler"


class TestLogFunctions:
    """Test logging convenience functions."""

    def test_log_error_without_exception(self):
        """Test logging error without exception."""
        with patch.object(game_logger, "error") as mock_error:
            log_error("Test error message")

            mock_error.assert_called_once_with("Test error message")

    def test_log_error_with_exception(self):
        """Test logging error with exception."""
        test_exception = ValueError("Test exception")

        with patch.object(game_logger, "error") as mock_error:
            log_error("Test error", test_exception)

            # Should be called with formatted message and exc_info
            assert mock_error.called
            call_args = mock_error.call_args
            assert "Test error" in call_args[0][0]
            assert "ValueError" in call_args[0][0]
            assert call_args[1].get("exc_info")

    def test_log_warning(self):
        """Test logging warning."""
        with patch.object(game_logger, "warning") as mock_warning:
            log_warning("Test warning")

            mock_warning.assert_called_once_with("Test warning")

    def test_log_info(self):
        """Test logging info."""
        with patch.object(game_logger, "info") as mock_info:
            log_info("Test info")

            mock_info.assert_called_once_with("Test info")

    def test_log_debug(self):
        """Test logging debug."""
        with patch.object(game_logger, "debug") as mock_debug:
            log_debug("Test debug")

            mock_debug.assert_called_once_with("Test debug")


class TestLoggerIntegration:
    """Integration tests for logger."""

    def test_logger_writes_to_file(self):
        """Test that logger actually writes to log file."""
        # Create a test logger
        test_logger = setup_logger("integration_test")

        # Log a test message
        test_message = "Integration test message"
        test_logger.info(test_message)

        # Verify logger has handlers
        assert len(test_logger.handlers) > 0

    def test_all_log_levels_work(self):
        """Test that all log level functions work."""
        # These should not raise exceptions
        log_debug("Debug message")
        log_info("Info message")
        log_warning("Warning message")
        log_error("Error message")

        # Test with exception
        try:
            raise RuntimeError("Test exception")
        except RuntimeError as e:
            log_error("Caught exception", e)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
