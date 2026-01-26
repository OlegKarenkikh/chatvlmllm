"""Pytest configuration and fixtures."""

import pytest
from PIL import Image
import streamlit as st


@pytest.fixture
def sample_image():
    """Create a sample RGB image for testing."""
    return Image.new('RGB', (100, 100), color='white')


@pytest.fixture
def sample_image_with_text():
    """Create a sample image with text for OCR testing."""
    from PIL import ImageDraw, ImageFont
    
    img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw simple text (without font file)
    draw.text((10, 40), "Test OCR Text", fill='black')
    
    return img


@pytest.fixture
def mock_streamlit_session():
    """Mock Streamlit session state."""
    class MockSessionState:
        def __init__(self):
            self.messages = []
            self.current_execution_mode = "vLLM (Рекомендуется)"
            self.max_tokens = 4096
            self.temperature = 0.7
    
    return MockSessionState()


@pytest.fixture
def sample_prompts():
    """Sample prompts for testing."""
    return {
        "ocr": "Прочитай текст с изображения",
        "chat": "Что на этом изображении?",
        "analysis": "Опиши подробно что ты видишь"
    }
