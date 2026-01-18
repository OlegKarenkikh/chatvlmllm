#!/usr/bin/env python3
"""
Быстрый тест проблемных моделей
"""

import sys
import time
from pathlib import Path
from PIL import Image
import torch

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from models.model_loader import ModelLoader
from utils.logger import logger

def quick_test_model(model_name: str) -> dict:
    """Test model quickly."""
    result = {
        "model": model_name,
        "status": "unknown",
        "load_time": 0,
        "process_time": 0,
        "error": None,
        "output_length": 0
    }
    
    try:
        # Create simple test image
        test_image_path = "test_simple.png"
        if not Path(test_image_path).exists():
            test_img = Image.new('RGB', (200, 100), color='white')
            from PIL import ImageDraw
            draw = ImageDraw.Draw(test_img)
            draw.text((10, 10), "Test", fill='black')
            test_img.save(test_image_path)
        
        image = Image.open(test_image_path)
        
        # Test loading
        logger.info(f"Loading {model_name}...")
        start_time = time.time()
        model = ModelLoader.load_model(model_name)
        load_time = time.time() - start_time
        result["load_time"] = load_time
        logger.info(f"Loaded {model_name} in {load_time:.2f}s")
        
        # Test processing (quick)
        logger.info(f"Processing with {model_name}...")
        process_start = time.time()
        
        if hasattr(model, 'process_image'):
            output = model.process_image(image)
        else:
            output = "No process_image method"
        
        process_time = time.time() - process_start
        result["process_time"] = process_time
        result["output_length"] = len(str(output))
        result["status"] = "success"
        
        logger.info(f"✅ {model_name}: Load={load_time:.2f}s, Process={process_time:.2f}s, Output={len(str(output))} chars")
        logger.info(f"Output: {str(output)[:100]}...")
        
        # Unload
        ModelLoader.unload_model(model_name)
        
    except Exception as e:
        result["error"] = str(e)
        result["status"] = "failed"
        logger.error(f"❌ {model_name}: {e}")
        
        # Force cleanup
        try:
            ModelLoader.unload_model(model_name)
        except:
            pass
    
    # Clear memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return result

def main():
    """Test problematic models."""
    logger.info("🚀 Quick test of problematic models...")
    
    # Test problematic models one by one
    models_to_test = [
        "got_ocr_ucas",
        "phi3_vision", 
        "dots_ocr"
    ]
    
    results = []
    
    for model_name in models_to_test:
        logger.info(f"\n{'='*50}")
        logger.info(f"🔄 Testing {model_name}...")
        logger.info(f"{'='*50}")
        
        result = quick_test_model(model_name)
        results.append(result)
        
        time.sleep(2)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("📊 PROBLEM MODELS TEST RESULTS")
    logger.info(f"{'='*60}")
    
    working = []
    failed = []
    
    for result in results:
        model_name = result["model"]
        
        if result["status"] == "success":
            working.append(model_name)
            logger.info(f"✅ {model_name:15} | Load: {result['load_time']:6.2f}s | Process: {result['process_time']:6.2f}s")
        else:
            failed.append(model_name)
            logger.info(f"❌ {model_name:15} | Error: {result['error']}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ WORKING: {len(working)}/{len(results)} - {', '.join(working)}")
    logger.info(f"❌ FAILED: {len(failed)}/{len(results)} - {', '.join(failed)}")
    logger.info(f"{'='*60}")
    
    return results

if __name__ == "__main__":
    main()