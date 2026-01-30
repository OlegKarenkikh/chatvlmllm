#!/usr/bin/env python3
"""
Тест всех моделей после исправлений
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

def test_model(model_name: str, test_image_path: str = "test_document.png") -> dict:
    """Test a single model."""
    result = {
        "model": model_name,
        "status": "unknown",
        "load_time": 0,
        "process_time": 0,
        "error": None,
        "output_length": 0,
        "vram_usage": 0
    }
    
    try:
        # Check if test image exists
        if not Path(test_image_path).exists():
            # Create a simple test image
            test_img = Image.new('RGB', (800, 600), color='white')
            test_img.save(test_image_path)
            logger.info(f"Created test image: {test_image_path}")
        
        # Load test image
        image = Image.open(test_image_path)
        
        # Measure load time
        start_time = time.time()
        
        try:
            model = ModelLoader.load_model(model_name)
            load_time = time.time() - start_time
            result["load_time"] = load_time
            
            # Get VRAM usage
            if torch.cuda.is_available():
                result["vram_usage"] = torch.cuda.memory_allocated() / 1024**3
            
            # Test processing
            process_start = time.time()
            
            if hasattr(model, 'process_image'):
                output = model.process_image(image)
            elif hasattr(model, 'extract_text'):
                output = model.extract_text(image)
            elif hasattr(model, 'chat'):
                output = model.chat(image, "Extract all text from this image")
            else:
                output = "No suitable method found"
            
            process_time = time.time() - process_start
            result["process_time"] = process_time
            result["output_length"] = len(str(output))
            result["status"] = "success"
            
            logger.info(f"✅ {model_name}: Load={load_time:.2f}s, Process={process_time:.2f}s, Output={len(str(output))} chars")
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "failed"
            logger.error(f"❌ {model_name}: {e}")
        
        finally:
            # Unload model to free memory
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
    """Test all models."""
    logger.info("🚀 Starting comprehensive model testing...")
    
    # List of all models to test
    models_to_test = [
        "got_ocr_hf",
        "got_ocr_ucas", 
        "qwen_vl_2b",
        "qwen3_vl_2b",
        "phi3_vision",
        "dots_ocr",
        "deepseek_ocr"
    ]
    
    results = []
    
    for model_name in models_to_test:
        logger.info(f"\n🔄 Testing {model_name}...")
        result = test_model(model_name)
        results.append(result)
        
        # Clear GPU memory between tests
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        time.sleep(2)  # Brief pause between tests
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("📊 FINAL TEST RESULTS")
    logger.info("="*60)
    
    working_models = []
    failed_models = []
    
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        model_name = result["model"]
        
        if result["status"] == "success":
            working_models.append(model_name)
            logger.info(f"{status_icon} {model_name:15} | Load: {result['load_time']:6.2f}s | Process: {result['process_time']:6.2f}s | Output: {result['output_length']:4d} chars | VRAM: {result['vram_usage']:4.1f}GB")
        else:
            failed_models.append(model_name)
            logger.info(f"{status_icon} {model_name:15} | ERROR: {result['error']}")
    
    logger.info("\n" + "="*60)
    logger.info(f"✅ WORKING MODELS ({len(working_models)}/{len(results)}): {', '.join(working_models)}")
    logger.info(f"❌ FAILED MODELS ({len(failed_models)}/{len(results)}): {', '.join(failed_models)}")
    logger.info("="*60)
    
    return results

if __name__ == "__main__":
    main()