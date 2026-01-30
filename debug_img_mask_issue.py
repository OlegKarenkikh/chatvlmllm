#!/usr/bin/env python3
"""
Debug script to understand the img_mask issue
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

def debug_processor():
    """Debug the processor to see what's happening with img_mask."""
    
    logger.info("🔍 Debugging img_mask issue")
    
    try:
        # Create a simple test image
        test_image = Image.new('RGB', (224, 224), color='white')
        
        # Load the model
        logger.info("Loading dots.ocr model...")
        config = {
            "model_path": "rednote-hilab/dots.ocr",
            "precision": "fp16",
            "device": "cuda",
            "max_new_tokens": 512
        }
        model = DotsOCRVideoProcessorFixedModel(config)
        model.load_model()
        
        # Test the processor directly
        logger.info("Testing processor directly...")
        
        # Call the processor
        inputs = model.processor(
            text="What do you see in this image?",
            images=test_image,
            return_tensors='pt'
        )
        
        logger.info(f"Processor output keys: {list(inputs.keys())}")
        
        for key, value in inputs.items():
            if isinstance(value, torch.Tensor):
                logger.info(f"{key}: shape={value.shape}, dtype={value.dtype}")
                if key == 'img_mask':
                    logger.info(f"img_mask sum: {value.sum()}")
                    logger.info(f"img_mask first 10 values: {value.flatten()[:10]}")
                elif key == 'pixel_values':
                    logger.info(f"pixel_values shape details: {value.shape}")
                elif key == 'image_grid_thw':
                    logger.info(f"image_grid_thw values: {value}")
            else:
                logger.info(f"{key}: {type(value)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Debug failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting img_mask debug")
    debug_processor()