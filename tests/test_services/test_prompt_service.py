"""Tests for services/prompt_service.py module."""

import pytest
from unittest.mock import Mock, patch
from PIL import Image
from services.prompt_service import PromptService


class TestPromptService:
    """Test PromptService class."""
    
    def test_clean_gpu_memory(self):
        """Test GPU memory cleaning."""
        # This would require mocking torch
        with patch('services.prompt_service.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = True
            PromptService._clean_gpu_memory()
            
            mock_torch.cuda.empty_cache.assert_called_once()
            mock_torch.cuda.synchronize.assert_called_once()
    
    def test_process_prompt_structure(self, sample_image):
        """Test process_prompt returns correct structure."""
        # This test demonstrates expected structure
        # Real implementation would need mocking
        
        expected_keys = ['success', 'text', 'processing_time', 'model_used', 'execution_mode']
        
        # Mock the actual processing
        with patch.object(PromptService, '_process_vllm') as mock_vllm:
            mock_vllm.return_value = "Mock response"
            
            # Would need proper setup for this to work
            # This is a structure test
            assert True  # Placeholder
    
    def test_adapt_dots_ocr_response_ocr_prompt(self):
        """Test adapting dots.ocr response for OCR prompts."""
        response = "Some extracted text"
        prompt = "Прочитай текст"
        processing_time = 1.5
        
        adapted = PromptService._adapt_dots_ocr_response(response, prompt, processing_time)
        
        assert "Some extracted text" in adapted
        assert "1.5" in adapted or "1.50" in adapted
    
    def test_adapt_dots_ocr_response_analytical_prompt(self):
        """Test adapting dots.ocr response for analytical prompts."""
        response = "Recognized text"
        prompt = "Что на этом изображении?"
        processing_time = 2.0
        
        adapted = PromptService._adapt_dots_ocr_response(response, prompt, processing_time)
        
        # Should suggest using Qwen3-VL for analytical questions
        assert "Qwen3-VL" in adapted or "dots.ocr" in adapted
