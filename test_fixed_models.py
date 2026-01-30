#!/usr/bin/env python3
"""
Быстрый тест исправленных моделей
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

def quick_test_model(model_name: str, timeout: int = 60) -> dict:
    """Quick test of a single model with timeout."""
    result = {
        "model": model_name,
        "status": "unknown",
        "load_time": 0,
        "error": None
    }
    
    try:
        # Create test image if needed
        test_image_path = "test_document.png"
        if not Path(test_image_path).exists():
            test_img = Image.new('RGB', (800, 600), color='white')
            test_img.save(test_image_path)
        
        image = Image.open(test_image_path)
        
        # Test loading with timeout
        start_time = time.time()
        
        try:
            model = ModelLoader.load_model(model_name)
            load_time = time.time() - start_time
            result["load_time"] = load_time
            
            # Quick processing test (just check if it doesn't crash)
            if hasattr(model, 'process_image'):
                output = model.process_image(image)
                result["status"] = "success"
                logger.info(f"✅ {model_name}: Load={load_time:.2f}s, Output={len(str(output))} chars")
            else:
                result["status"] = "no_method"
                logger.warning(f"⚠️ {model_name}: No process_image method")
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "failed"
            logger.error(f"❌ {model_name}: {e}")
        
        finally:
            # Unload model
            try:
                ModelLoader.unload_model(model_name)
            except:
                pass
    
    except Exception as e:
        result["error"] = str(e)
        result["status"] = "failed"
        logger.error(f"❌ {model_name} setup failed: {e}")
    
    return result

def main():
    """Test problematic models."""
    logger.info("🚀 Quick test of fixed models...")
    
    # Test only the problematic models
    models_to_test = [
        "got_ocr_ucas",  # Fixed CUDA issue
        "dots_ocr",      # Fixed NoneType issue
        "phi3_vision"    # Fixed Flash Attention issue
    ]
    
    results = []
    
    for model_name in models_to_test:
        logger.info(f"\n🔄 Quick testing {model_name}...")
        result = quick_test_model(model_name, timeout=120)
        results.append(result)
        
        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        time.sleep(1)
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("📊 QUICK TEST RESULTS")
    logger.info("="*50)
    
    working = []
    failed = []
    
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        model_name = result["model"]
        
        if result["status"] == "success":
            working.append(model_name)
            logger.info(f"{status_icon} {model_name:15} | Load: {result['load_time']:6.2f}s")
        else:
            failed.append(model_name)
            logger.info(f"{status_icon} {model_name:15} | ERROR: {result['error']}")
    
    logger.info("\n" + "="*50)
    logger.info(f"✅ WORKING: {len(working)}/{len(results)} - {', '.join(working)}")
    logger.info(f"❌ FAILED: {len(failed)}/{len(results)} - {', '.join(failed)}")
    logger.info("="*50)
    
    return results

if __name__ == "__main__":
    main()