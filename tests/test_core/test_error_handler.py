"""Tests for core/error_handler.py module."""

import pytest
from core.error_handler import ErrorHandler


class TestErrorHandler:
    """Test ErrorHandler class."""
    
    def test_is_cuda_error(self):
        """Test CUDA error detection."""
        cuda_error = Exception("CUDA error: out of memory")
        assert ErrorHandler.is_cuda_error(cuda_error) == True
        
        normal_error = Exception("Some other error")
        assert ErrorHandler.is_cuda_error(normal_error) == False
    
    def test_is_model_loading_error(self):
        """Test model loading error detection."""
        model_error = Exception("video_processor is None")
        assert ErrorHandler.is_model_loading_error(model_error) == True
        
        normal_error = Exception("Some other error")
        assert ErrorHandler.is_model_loading_error(normal_error) == False
    
    def test_is_out_of_memory_error(self):
        """Test OOM error detection."""
        oom_error = Exception("CUDA out of memory")
        assert ErrorHandler.is_out_of_memory_error(oom_error) == True
        
        normal_error = Exception("Some other error")
        assert ErrorHandler.is_out_of_memory_error(normal_error) == False
    
    def test_handle_cuda_error(self):
        """Test CUDA error handling."""
        cuda_error = Exception("CUDA error occurred")
        error_msg, recommendation = ErrorHandler.handle_error(cuda_error, "test")
        
        assert "Критическая ошибка GPU" in error_msg
        assert "Рекомендация" in recommendation
    
    def test_handle_oom_error(self):
        """Test OOM error handling."""
        oom_error = Exception("out of memory")
        error_msg, recommendation = ErrorHandler.handle_error(oom_error)
        
        assert "Недостаточно памяти GPU" in error_msg
        assert "Рекомендация" in recommendation
    
    def test_create_error_response(self):
        """Test error response creation."""
        error = Exception("Test error")
        response = ErrorHandler.create_error_response(error, "testing")
        
        assert isinstance(response, str)
        assert len(response) > 0
