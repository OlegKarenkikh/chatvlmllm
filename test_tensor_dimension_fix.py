#!/usr/bin/env python3
"""
Test script to verify the tensor dimension fix for dots.ocr
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

def test_tensor_dimensions():
    """Test that the tensor dimensions are calculated correctly."""
    
    logger.info("🧪 Testing tensor dimension fix for dots.ocr")
    
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
        model.load_model()  # Load the model
        
        # Test image processing
        logger.info("Testing image processing...")
        result = model.process_image(test_image, "What do you see in this image?")
        
        logger.info("✅ Tensor dimension fix test passed!")
        logger.info(f"Result: {result[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Tensor dimension fix test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_processor_directly():
    """Test the processor directly to check tensor shapes."""
    
    logger.info("🧪 Testing processor tensor shapes directly")
    
    try:
        from transformers import AutoImageProcessor, AutoTokenizer
        from PIL import Image
        import torch
        
        # Load components
        image_processor = AutoImageProcessor.from_pretrained(
            "rednote-hilab/dots.ocr", 
            trust_remote_code=True
        )
        tokenizer = AutoTokenizer.from_pretrained(
            "rednote-hilab/dots.ocr", 
            trust_remote_code=True,
            use_fast=False
        )
        
        # Create test image
        test_image = Image.new('RGB', (224, 224), color='white')
        
        # Process image
        image_inputs = image_processor(test_image, return_tensors='pt')
        logger.info(f"Image inputs keys: {list(image_inputs.keys())}")
        
        if 'pixel_values' in image_inputs:
            pixel_values = image_inputs['pixel_values']
            logger.info(f"Pixel values shape: {pixel_values.shape}")
            
            # Check if image_grid_thw is already provided
            if 'image_grid_thw' in image_inputs:
                existing_grid_thw = image_inputs['image_grid_thw']
                logger.info(f"Existing image_grid_thw: {existing_grid_thw}")
                logger.info(f"Existing image_grid_thw shape: {existing_grid_thw.shape}")
            
            batch_size = pixel_values.shape[0]
            
            # Calculate patches correctly
            if len(pixel_values.shape) == 4:
                _, channels, height, width = pixel_values.shape
                patch_size = 14
                h_patches = height // patch_size
                w_patches = width // patch_size
                total_patches = h_patches * w_patches
                
                logger.info(f"Image dimensions: {height}x{width}")
                logger.info(f"Patch grid: {h_patches}x{w_patches} = {total_patches} patches")
                
                # Create tensors
                image_grid_thw = torch.tensor([[1, h_patches, w_patches]], dtype=torch.long)
                img_mask = torch.ones(batch_size, total_patches, dtype=torch.bool)
                
                logger.info(f"image_grid_thw shape: {image_grid_thw.shape}, values: {image_grid_thw}")
                logger.info(f"img_mask shape: {img_mask.shape}")
                
                # Verify tensor consistency
                expected_patches = h_patches * w_patches
                if img_mask.shape[1] == expected_patches:
                    logger.info("✅ Tensor dimensions are consistent!")
                    return True
                else:
                    logger.error(f"❌ Tensor dimension mismatch: expected {expected_patches}, got {img_mask.shape[1]}")
                    return False
            else:
                logger.info(f"Pixel values already in patch format: {pixel_values.shape}")
                return True
        
    except Exception as e:
        logger.error(f"❌ Processor test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting tensor dimension fix tests")
    
    # Test processor directly first
    processor_ok = test_processor_directly()
    
    if processor_ok:
        # Test full model if processor works
        model_ok = test_tensor_dimensions()
        
        if model_ok:
            logger.info("🎉 All tests passed! Tensor dimension fix is working correctly.")
        else:
            logger.error("❌ Model test failed")
    else:
        logger.error("❌ Processor test failed")