#!/usr/bin/env python3
"""
Комплексный тест всех моделей с детальной диагностикой
"""

import sys
import time
from pathlib import Path
from PIL import Image
import torch
import traceback

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.model_loader import ModelLoader
from utils.logger import logger

def comprehensive_test_model(model_name: str) -> dict:
    """Comprehensive test of a single model."""
    result = {
        "model": model_name,
        "status": "unknown",
        "load_time": 0,
        "process_time": 0,
        "error": None,
        "output_length": 0,
        "detailed_error": None
    }
    
    try:
        # Create test image if needed
        test_image_path = "test_document.png"
        if not Path(test_image_path).exists():
            test_img = Image.new('RGB', (800, 600), color='white')
            # Add some text to the image
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(test_img)
            try:
                font = ImageFont.load_default()
                draw.text((50, 50), "Test Document\nSample Text\n123 456", fill='black', font=font)
            except:
                draw.text((50, 50), "Test Document\nSample Text\n123 456", fill='black')
            test_img.save(test_image_path)
        
        image = Image.open(test_image_path)
        
        # Test loading
        start_time = time.time()
        
        try:
            logger.info(f"Loading {model_name}...")
            model = ModelLoader.load_model(model_name)
            load_time = time.time() - start_time
            result["load_time"] = load_time
            
            logger.info(f"Model {model_name} loaded in {load_time:.2f}s")
            
            # Test processing
            process_start = time.time()
            
            try:
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
                logger.info(f"Output preview: {str(output)[:100]}...")
                
            except Exception as process_error:
                result["error"] = f"Processing error: {str(process_error)}"
                result["detailed_error"] = traceback.format_exc()
                result["status"] = "process_failed"
                logger.error(f"❌ {model_name} processing failed: {process_error}")
                logger.error(f"Detailed error: {traceback.format_exc()}")
            
        except Exception as load_error:
            result["error"] = f"Loading error: {str(load_error)}"
            result["detailed_error"] = traceback.format_exc()
            result["status"] = "load_failed"
            logger.error(f"❌ {model_name} loading failed: {load_error}")
            logger.error(f"Detailed error: {traceback.format_exc()}")
        
        finally:
            # Unload model
            try:
                ModelLoader.unload_model(model_name)
                logger.info(f"Model {model_name} unloaded")
            except Exception as unload_error:
                logger.warning(f"Failed to unload {model_name}: {unload_error}")
    
    except Exception as e:
        result["error"] = f"Setup error: {str(e)}"
        result["detailed_error"] = traceback.format_exc()
        result["status"] = "setup_failed"
        logger.error(f"❌ {model_name} setup failed: {e}")
    
    return result

def main():
    """Test all models comprehensively."""
    logger.info("🚀 Starting comprehensive model testing...")
    
    # All models to test
    config = ModelLoader.load_config()
    models_to_test = list(config.get("models", {}).keys())
    
    results = []
    
    for model_name in models_to_test:
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 Testing {model_name}...")
        logger.info(f"{'='*60}")
        
        result = comprehensive_test_model(model_name)
        results.append(result)
        
        # Clear GPU memory between tests
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        time.sleep(2)  # Brief pause between tests
    
    # Print comprehensive summary
    logger.info("\n" + "="*80)
    logger.info("📊 COMPREHENSIVE TEST RESULTS")
    logger.info("="*80)
    
    working_models = []
    failed_models = []
    
    for result in results:
        model_name = result["model"]
        status = result["status"]
        
        if status == "success":
            working_models.append(model_name)
            logger.info(f"✅ {model_name:15} | Load: {result['load_time']:6.2f}s | Process: {result['process_time']:6.2f}s | Output: {result['output_length']:4d} chars")
        else:
            failed_models.append(model_name)
            logger.info(f"❌ {model_name:15} | Status: {status} | Error: {result['error']}")
            if result['detailed_error']:
                logger.info(f"   Detailed error: {result['detailed_error'][:200]}...")
    
    logger.info("\n" + "="*80)
    logger.info(f"✅ WORKING MODELS ({len(working_models)}/{len(results)}): {', '.join(working_models)}")
    logger.info(f"❌ FAILED MODELS ({len(failed_models)}/{len(results)}): {', '.join(failed_models)}")
    logger.info("="*80)
    
    # Detailed failure analysis
    if failed_models:
        logger.info("\n📋 FAILURE ANALYSIS:")
        for result in results:
            if result["status"] != "success":
                logger.info(f"\n🔍 {result['model']}:")
                logger.info(f"   Status: {result['status']}")
                logger.info(f"   Error: {result['error']}")
                if result['detailed_error']:
                    logger.info(f"   Stack trace: {result['detailed_error']}")
    
    return results

if __name__ == "__main__":
    main()