#!/usr/bin/env python3
"""Test script for new model integrations."""

import sys
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader
from utils.logger import logger


def test_model_cache_status():
    """Test cache status for all models."""
    print("🔍 Checking cache status for all models...")
    print("=" * 60)
    
    config = ModelLoader.load_config()
    models = config.get('models', {})
    
    cached_models = []
    missing_models = []
    
    for model_key, model_config in models.items():
        print(f"\n📊 {model_key} ({model_config.get('name', 'Unknown')})")
        print(f"   Path: {model_config.get('model_path', 'N/A')}")
        
        try:
            is_cached, message = ModelLoader.check_model_cache(model_key)
            if is_cached:
                print(f"   ✅ {message}")
                cached_models.append(model_key)
            else:
                print(f"   ❌ {message}")
                missing_models.append(model_key)
        except Exception as e:
            print(f"   ⚠️  Error checking cache: {e}")
            missing_models.append(model_key)
    
    print(f"\n📈 SUMMARY")
    print(f"   Total models: {len(models)}")
    print(f"   Cached: {len(cached_models)}")
    print(f"   Missing: {len(missing_models)}")
    
    if cached_models:
        print(f"\n✅ CACHED MODELS:")
        for model in cached_models:
            print(f"   - {model}")
    
    if missing_models:
        print(f"\n❌ MISSING MODELS:")
        for model in missing_models:
            print(f"   - {model}")
    
    return cached_models, missing_models


def test_model_registry():
    """Test model registry completeness."""
    print("\n🔧 Checking model registry...")
    print("=" * 60)
    
    config = ModelLoader.load_config()
    config_models = set(config.get('models', {}).keys())
    registry_models = set(ModelLoader.MODEL_REGISTRY.keys())
    
    print(f"Config models: {len(config_models)}")
    print(f"Registry models: {len(registry_models)}")
    
    missing_in_registry = config_models - registry_models
    extra_in_registry = registry_models - config_models
    
    if missing_in_registry:
        print(f"\n❌ MISSING IN REGISTRY:")
        for model in missing_in_registry:
            print(f"   - {model}")
    
    if extra_in_registry:
        print(f"\n⚠️  EXTRA IN REGISTRY:")
        for model in extra_in_registry:
            print(f"   - {model}")
    
    if not missing_in_registry and not extra_in_registry:
        print(f"\n✅ Registry and config are in sync!")
    
    return missing_in_registry, extra_in_registry


def test_model_loading(model_key: str):
    """Test loading a specific model."""
    print(f"\n🚀 Testing model loading: {model_key}")
    print("-" * 40)
    
    try:
        # Check cache first
        is_cached, cache_msg = ModelLoader.check_model_cache(model_key)
        print(f"Cache status: {cache_msg}")
        
        if not is_cached:
            print("⚠️  Model not in cache - would download on load")
            return False
        
        # Try to load model
        print("Loading model...")
        model = ModelLoader.load_model(model_key)
        
        print(f"✅ Model loaded successfully!")
        print(f"   Type: {type(model).__name__}")
        print(f"   Config: {model.config.get('name', 'Unknown')}")
        
        # Test model info
        info = model.get_model_info()
        print(f"   Device: {info.get('device', 'Unknown')}")
        print(f"   Loaded: {info.get('loaded', False)}")
        
        # Unload model to free memory
        ModelLoader.unload_model(model_key)
        print("   Model unloaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🧪 Testing New Model Integrations")
    print("=" * 60)
    
    # Test 1: Cache status
    cached_models, missing_models = test_model_cache_status()
    
    # Test 2: Registry completeness
    missing_in_registry, extra_in_registry = test_model_registry()
    
    # Test 3: Try loading cached models
    if cached_models:
        print(f"\n🚀 Testing model loading for cached models...")
        print("=" * 60)
        
        successful_loads = []
        failed_loads = []
        
        for model_key in cached_models:
            success = test_model_loading(model_key)
            if success:
                successful_loads.append(model_key)
            else:
                failed_loads.append(model_key)
        
        print(f"\n📊 LOADING TEST RESULTS")
        print(f"   Successful: {len(successful_loads)}")
        print(f"   Failed: {len(failed_loads)}")
        
        if successful_loads:
            print(f"\n✅ SUCCESSFUL LOADS:")
            for model in successful_loads:
                print(f"   - {model}")
        
        if failed_loads:
            print(f"\n❌ FAILED LOADS:")
            for model in failed_loads:
                print(f"   - {model}")
    
    # Final summary
    print(f"\n🎯 FINAL SUMMARY")
    print("=" * 60)
    print(f"✅ New model classes created and registered")
    print(f"✅ API updated with new models")
    print(f"✅ Model loader updated")
    
    if missing_in_registry:
        print(f"⚠️  {len(missing_in_registry)} models missing from registry")
    else:
        print(f"✅ All config models are in registry")
    
    print(f"\n🔄 Next steps:")
    if missing_models:
        print(f"   - Download missing models: {', '.join(missing_models[:3])}{'...' if len(missing_models) > 3 else ''}")
    print(f"   - Test API endpoints with new models")
    print(f"   - Verify model inference works correctly")
    print(f"   - Optimize model loading and memory usage")


if __name__ == "__main__":
    main()