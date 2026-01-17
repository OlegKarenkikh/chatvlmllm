#!/usr/bin/env python3
"""Quick test of working models."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def test_working_models():
    """Test models that should work."""
    working_models = [
        "qwen_vl_2b",
        "qwen3_vl_2b", 
        "got_ocr_hf",
        "dots_ocr",
        "phi3_vision",
        "got_ocr_ucas"
    ]
    
    print("🧪 Testing Working Models")
    print("=" * 50)
    
    for model_key in working_models:
        print(f"\n🚀 Testing {model_key}...")
        try:
            # Check cache
            is_cached, msg = ModelLoader.check_model_cache(model_key)
            if not is_cached:
                print(f"   ❌ Not cached: {msg}")
                continue
                
            # Load model
            model = ModelLoader.load_model(model_key)
            print(f"   ✅ Loaded successfully: {type(model).__name__}")
            
            # Unload
            ModelLoader.unload_model(model_key)
            print(f"   🔄 Unloaded")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print(f"\n✅ Test complete!")


if __name__ == "__main__":
    test_working_models()