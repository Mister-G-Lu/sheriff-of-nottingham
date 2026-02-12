"""
Game Logging System
Handles error logging to file instead of displaying to users
"""

import logging
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "sheriff_game") -> logging.Logger:
    """
    Set up a logger that writes to both file and console (for development).

    Args:
        name: Logger name

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # File handler - logs everything to file
    log_file = log_dir / f"game_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Only add console handler if not in pygame mode (check if DISPLAY is set or running in terminal)
    # This prevents logs from appearing in the pygame window
    # Console handler disabled by default - check logs/ directory for errors

    return logger


# Global logger instance
game_logger = setup_logger()


def log_error(message: str, exception: Exception = None):
    """
    Log an error message with optional exception details.

    Args:
        message: Error message to log
        exception: Optional exception object
    """
    if exception:
        game_logger.error(
            f"{message}: {type(exception).__name__}: {str(exception)}", exc_info=True
        )
    else:
        game_logger.error(message)


def log_warning(message: str):
    """Log a warning message."""
    game_logger.warning(message)


def log_info(message: str):
    """Log an info message."""
    game_logger.info(message)


def log_debug(message: str):
    """Log a debug message."""
    game_logger.debug(message)
