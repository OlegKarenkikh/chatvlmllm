"""Tests for model classes."""

import pytest
from PIL import Image
import numpy as np
from models.base_model import BaseVLMModel
from models.model_loader import ModelLoader


class TestModelLoader:
    """Test ModelLoader functionality."""
    
    def test_load_config(self):
        """Test configuration loading."""
        config = ModelLoader.load_config("config.yaml")
        assert "models" in config
        assert "app" in config
        assert "ocr" in config
    
    def test_get_available_models(self):
        """Test getting available models."""
        models = ModelLoader.get_available_models()
        assert "got_ocr" in models
        assert "qwen_vl_2b" in models
        assert "qwen_vl_7b" in models
    
    def test_model_info(self):
        """Test model information retrieval."""
        models = ModelLoader.get_available_models()
        got_ocr = models["got_ocr"]
        assert "name" in got_ocr
        assert "model_id" in got_ocr
        assert "precision" in got_ocr


class TestImageProcessor:
    """Test image processing utilities."""
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample test image."""
        # Create a simple RGB image
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        return Image.fromarray(img_array)
    
    def test_resize_image(self, sample_image):
        """Test image resizing."""
        from utils.image_processor import ImageProcessor
        
        resized = ImageProcessor.resize_image(sample_image, max_dimension=50)
        assert resized.size[0] <= 50
        assert resized.size[1] <= 50
    
    def test_enhance_image(self, sample_image):
        """Test image enhancement."""
        from utils.image_processor import ImageProcessor
        
        enhanced = ImageProcessor.enhance_image(sample_image)
        assert enhanced.size == sample_image.size
        assert enhanced.mode == sample_image.mode


class TestTextExtractor:
    """Test text extraction utilities."""
    
    def test_clean_text(self):
        """Test text cleaning."""
        from utils.text_extractor import TextExtractor
        
        dirty_text = "  This   is   \n\n\n  dirty   text  "
        clean = TextExtractor.clean_text(dirty_text)
        assert "  " not in clean
        assert clean == "This is \n dirty text"
    
    def test_extract_numbers(self):
        """Test number extraction."""
        from utils.text_extractor import TextExtractor
        
        text = "Invoice #12345 for $1,234.56"
        numbers = TextExtractor.extract_numbers(text)
        assert "12345" in numbers
        assert "1234.56" in numbers
    
    def test_extract_dates(self):
        """Test date extraction."""
        from utils.text_extractor import TextExtractor
        
        text = "Date: 15/01/2026 or 2026-01-15"
        dates = TextExtractor.extract_dates(text)
        assert len(dates) >= 1


class TestFieldParser:
    """Test field parsing utilities."""
    
    def test_parse_invoice_fields(self):
        """Test invoice field extraction."""
        from utils.field_parser import FieldParser
        
        text = """
        Invoice #INV-2026-001
        Invoice Date: 15/01/2026
        Total: $1,234.56
        """
        
        fields = FieldParser.parse_invoice_fields(text)
        assert "Invoice Number" in fields
        assert "Invoice Date" in fields
        assert "Total Amount" in fields
    
    def test_normalize_amount(self):
        """Test amount normalization."""
        from utils.field_parser import FieldParser
        
        assert FieldParser.normalize_amount("$1,234.56") == 1234.56
        assert FieldParser.normalize_amount("£100.00") == 100.00
        assert FieldParser.normalize_amount("1.234,56") == 1234.56


if __name__ == "__main__":
    pytest.main([__file__])