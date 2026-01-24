#!/usr/bin/env python3
"""
Simple test to verify dots.ocr works with the fixed processor
"""

import sys
import os
import traceback
from PIL import Image
import torch

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.dots_ocr_video_processor_fixed import DotsOCRVideoProcessorFixedModel
from utils.logger import logger

def test_simple_ocr():
    """Test simple OCR functionality."""
    
    logger.info("🧪 Testing simple OCR with dots.ocr")
    
    try:
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image with simple text
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        draw.text((10, 30), "Hello World", fill='black', font=font)
        
        # Load the model
        logger.info("Loading dots.ocr model...")
        config = {
            "model_path": "rednote-hilab/dots.ocr",
            "precision": "fp16",
            "device": "cuda",
            "max_new_tokens": 50
        }
        model = DotsOCRVideoProcessorFixedModel(config)
        model.load_model()
        
        # Test OCR
        logger.info("Testing OCR...")
        result = model.process_image(img, "What text is in this image?")
        
        logger.info(f"✅ OCR Result: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Simple OCR test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting simple OCR test")
    success = test_simple_ocr()
    
    if success:
        logger.info("🎉 Simple OCR test passed!")
    else:
        logger.error("❌ Simple OCR test failed")