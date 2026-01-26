"""Tests for core/logger.py module."""

import pytest
import logging
from pathlib import Path
from core.logger import setup_logger, get_logger, LoggerContext


class TestLogger:
    """Test logger functionality."""
    
    def test_setup_logger_console_only(self):
        """Test logger setup with console handler only."""
        logger = setup_logger('test_console', log_to_console=True)
        
        assert logger.name == 'test_console'
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_setup_logger_with_file(self, tmp_path):
        """Test logger setup with file handler."""
        log_file = tmp_path / "test.log"
        logger = setup_logger('test_file', log_file=str(log_file))
        
        logger.info("Test message")
        
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content
    
    def test_logger_context(self):
        """Test logger context manager."""
        logger_name = 'test_context'
        logger = setup_logger(logger_name, level=logging.INFO)
        
        # Check initial level
        assert logger.level == logging.INFO
        
        # Use context to temporarily change level
        with LoggerContext(logger_name, level=logging.DEBUG):
            temp_logger = logging.getLogger(logger_name)
            assert temp_logger.level == logging.DEBUG
        
        # Check level restored
        assert logger.level == logging.INFO
    
    def test_get_logger(self):
        """Test getting existing logger."""
        logger1 = setup_logger('test_get')
        logger2 = get_logger('test_get')
        
        assert logger1 is logger2
