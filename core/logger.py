"""Structured logging module for ChatVLMLLM.

Provides centralized logging configuration with file and console handlers,
formatted output, and log rotation.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string with colors
        """
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    log_to_console: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """Setup and configure logger with file and console handlers.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Path to log file (optional)
        level: Logging level (default: INFO)
        log_to_console: Whether to log to console (default: True)
        max_bytes: Max file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> from core.logger import setup_logger
        >>> logger = setup_logger(__name__, 'logs/app.log')
        >>> logger.info("Application started")
        >>> logger.error("Error occurred", exc_info=True)
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Format string
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Console handler with colors
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(log_format, datefmt=date_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get existing logger or create new one with default config.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


class LoggerContext:
    """Context manager for temporary logger configuration.
    
    Example:
        >>> with LoggerContext('myapp', level=logging.DEBUG):
        ...     logger = get_logger('myapp')
        ...     logger.debug("Debug message")  # Will be logged
    """
    
    def __init__(self, name: str, level: int = logging.INFO):
        """Initialize logger context.
        
        Args:
            name: Logger name
            level: Temporary logging level
        """
        self.name = name
        self.new_level = level
        self.old_level = None
    
    def __enter__(self):
        """Enter context - set new level."""
        logger = logging.getLogger(self.name)
        self.old_level = logger.level
        logger.setLevel(self.new_level)
        return logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - restore old level."""
        logger = logging.getLogger(self.name)
        if self.old_level is not None:
            logger.setLevel(self.old_level)


# Default application logger
app_logger = setup_logger('chatvlmllm', 'logs/app.log')


# Convenience functions
def log_model_load(model_name: str, execution_mode: str):
    """Log model loading event.
    
    Args:
        model_name: Name of the model
        execution_mode: Execution mode (vLLM/Transformers)
    """
    app_logger.info(f"Loading model: {model_name} (mode: {execution_mode})")


def log_inference(model_name: str, processing_time: float, success: bool):
    """Log inference event.
    
    Args:
        model_name: Name of the model
        processing_time: Time taken for inference
        success: Whether inference was successful
    """
    status = "SUCCESS" if success else "FAILED"
    app_logger.info(
        f"Inference {status}: {model_name} - {processing_time:.2f}s"
    )


def log_error(error: Exception, context: str = ""):
    """Log error with context.
    
    Args:
        error: Exception that occurred
        context: Context where error occurred
    """
    context_str = f" in {context}" if context else ""
    app_logger.error(f"Error{context_str}: {str(error)}", exc_info=True)