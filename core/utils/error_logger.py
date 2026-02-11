"""
Error Logging System

Logs all exceptions and errors to the logs directory for easier debugging.
"""

import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime


def setup_error_logging():
    """
    Set up comprehensive error logging to logs directory.
    
    Creates:
    - logs/game_YYYYMMDD_HHMMSS.log - Main game log
    - logs/errors_YYYYMMDD_HHMMSS.log - Error-only log
    """
    # Create logs directory
    logs_dir = Path(__file__).parent.parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Generate timestamp for log files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Main log file (all messages)
    main_log_file = logs_dir / f'game_{timestamp}.log'
    
    # Error log file (errors only)
    error_log_file = logs_dir / f'errors_{timestamp}.log'
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Main log file handler (all messages, DEBUG and above)
    main_handler = logging.FileHandler(main_log_file, encoding='utf-8')
    main_handler.setLevel(logging.DEBUG)
    main_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(main_handler)
    
    # Error log file handler (errors only, ERROR and above)
    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Console handler (INFO and above, for user visibility)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Log startup message
    logging.info("=" * 70)
    logging.info("Sheriff of Nottingham - Game Started")
    logging.info(f"Main log: {main_log_file}")
    logging.info(f"Error log: {error_log_file}")
    logging.info("=" * 70)
    
    return main_log_file, error_log_file


def log_exception(exc_type, exc_value, exc_traceback):
    """
    Custom exception handler that logs all uncaught exceptions.
    
    This is set as sys.excepthook to catch all unhandled exceptions.
    """
    # Don't log keyboard interrupts (Ctrl+C)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the exception
    logging.error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Also print to stderr for immediate visibility
    print("\n" + "=" * 70, file=sys.stderr)
    print("ERROR: An exception occurred during gameplay", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("Check the logs directory for detailed error information.", file=sys.stderr)
    print("=" * 70 + "\n", file=sys.stderr)


def install_exception_handler():
    """Install the custom exception handler."""
    sys.excepthook = log_exception


def log_game_event(event_type: str, message: str, **kwargs):
    """
    Log a game event with additional context.
    
    Args:
        event_type: Type of event (e.g., 'merchant_arrival', 'inspection', 'bribe')
        message: Event message
        **kwargs: Additional context to log
    """
    context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    if context:
        logging.info(f"[{event_type}] {message} | {context}")
    else:
        logging.info(f"[{event_type}] {message}")


def log_error(error_type: str, message: str, exception: Exception = None):
    """
    Log an error with context.
    
    Args:
        error_type: Type of error (e.g., 'portrait_load', 'merchant_load')
        message: Error message
        exception: Optional exception object
    """
    if exception:
        logging.error(f"[{error_type}] {message}", exc_info=exception)
    else:
        logging.error(f"[{error_type}] {message}")


def log_debug(component: str, message: str, **kwargs):
    """
    Log debug information.
    
    Args:
        component: Component name (e.g., 'ui', 'ai', 'game_manager')
        message: Debug message
        **kwargs: Additional debug context
    """
    context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    if context:
        logging.debug(f"[{component}] {message} | {context}")
    else:
        logging.debug(f"[{component}] {message}")


def cleanup_old_logs(keep_count: int = 10):
    """
    Clean up old log files, keeping only the most recent ones.
    
    Args:
        keep_count: Number of recent log files to keep
    """
    logs_dir = Path(__file__).parent.parent.parent / 'logs'
    
    if not logs_dir.exists():
        return
    
    # Get all log files sorted by modification time
    log_files = sorted(logs_dir.glob('*.log'), key=lambda p: p.stat().st_mtime, reverse=True)
    
    # Delete old files
    for log_file in log_files[keep_count:]:
        try:
            log_file.unlink()
            logging.debug(f"Deleted old log file: {log_file.name}")
        except Exception as e:
            logging.warning(f"Failed to delete old log file {log_file.name}: {e}")


# Convenience function to get logger for a module
def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(name)
