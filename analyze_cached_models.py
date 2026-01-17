#!/usr/bin/env python3
"""Analyze all cached HuggingFace models and check compatibility."""

import os
import json
from pathlib import Path
from transformers import AutoConfig
import yaml

def get_cache_dir():
    """Get HuggingFace cache directory."""
    return Path.home() / ".cache" / "huggingface" / "hub"

def analyze_model(model_path):
    """Analyze a single model."""
    try:
        # Try to load config
        config_path = model_path / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            model_type = config.get('model_type', 'unknown')
            architectures = config.get('architectures', [])
            
            # Check if it's a vision-language model
            is_vlm = any(arch for arch in architectures if any(keyword in arch.lower() 
                        for keyword in ['vision', 'vlm', 'multimodal', 'qwen', 'phi', 'idefics', 'vila']))
            
            # Check if it's an OCR model
            is_ocr = any(keyword in str(model_path).lower() 
                        for keyword in ['ocr', 'got', 'dots'])
            
            return {
                'model_type': model_type,
                'architectures': architectures,
                'is_vlm': is_vlm,
                'is_ocr': is_ocr,
                'config': config
            }
    except Exception as e:
        return {'error': str(e)}
    
    return {'error': 'No config found'}

def get_model_size(model_path):
    """Calculate model size in GB."""
    total_size = 0
    for root, dirs, files in os.walk(model_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    return total_size / (1024**3)  # Convert to GB

def main():
    """Main function."""
    print("🔍 Analyzing all cached HuggingFace models...")
    print("=" * 60)
    
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        print("❌ HuggingFace cache directory not found!")
        return
    
    # Find all model directories
    model_dirs = [d for d in cache_dir.iterdir() if d.is_dir() and d.name.startswith('models--')]
    
    print(f"📁 Found {len(model_dirs)} cached models")
    print()
    
    vlm_models = []
    ocr_models = []
    other_models = []
    total_size = 0
    
    for model_dir in sorted(model_dirs):
        # Extract model name
        model_name = model_dir.name.replace('models--', '').replace('--', '/')
        
        # Find the actual model files (in snapshots)
        snapshots_dir = model_dir / "snapshots"
        if not snapshots_dir.exists():
            continue
            
        # Get the latest snapshot
        snapshot_dirs = [d for d in snapshots_dir.iterdir() if d.is_dir()]
        if not snapshot_dirs:
            continue
            
        latest_snapshot = max(snapshot_dirs, key=lambda x: x.stat().st_mtime)
        
        # Calculate size
        size_gb = get_model_size(model_dir)
        total_size += size_gb
        
        # Analyze model
        analysis = analyze_model(latest_snapshot)
        
        model_info = {
            'name': model_name,
            'path': str(model_dir),
            'size_gb': round(size_gb, 2),
            'analysis': analysis
        }
        
        # Categorize
        if analysis.get('is_vlm'):
            vlm_models.append(model_info)
        elif analysis.get('is_ocr'):
            ocr_models.append(model_info)
        else:
            other_models.append(model_info)
    
    # Print results
    print("🤖 VISION-LANGUAGE MODELS (VLM)")
    print("-" * 40)
    for model in vlm_models:
        print(f"📊 {model['name']}")
        print(f"   Size: {model['size_gb']} GB")
        if 'architectures' in model['analysis']:
            print(f"   Architecture: {', '.join(model['analysis']['architectures'])}")
        print(f"   Type: {model['analysis'].get('model_type', 'unknown')}")
        print()
    
    print("🔍 OCR MODELS")
    print("-" * 40)
    for model in ocr_models:
        print(f"📊 {model['name']}")
        print(f"   Size: {model['size_gb']} GB")
        if 'architectures' in model['analysis']:
            print(f"   Architecture: {', '.join(model['analysis']['architectures'])}")
        print(f"   Type: {model['analysis'].get('model_type', 'unknown')}")
        print()
    
    print("📦 OTHER MODELS")
    print("-" * 40)
    for model in other_models:
        print(f"📊 {model['name']}")
        print(f"   Size: {model['size_gb']} GB")
        if 'architectures' in model['analysis']:
            print(f"   Architecture: {', '.join(model['analysis']['architectures'])}")
        print(f"   Type: {model['analysis'].get('model_type', 'unknown')}")
        print()
    
    # Summary
    print("📈 SUMMARY")
    print("-" * 40)
    print(f"Total models: {len(model_dirs)}")
    print(f"VLM models: {len(vlm_models)}")
    print(f"OCR models: {len(ocr_models)}")
    print(f"Other models: {len(other_models)}")
    print(f"Total cache size: {round(total_size, 2)} GB")
    print()
    
    # Recommendations
    print("💡 INTEGRATION RECOMMENDATIONS")
    print("-" * 40)
    
    # Check which models could be added to config
    current_config_path = Path("config.yaml")
    if current_config_path.exists():
        with open(current_config_path, 'r', encoding='utf-8') as f:
            current_config = yaml.safe_load(f)
        
        current_models = set(current_config.get('models', {}).keys())
        
        print("🔧 Models that could be added to config.yaml:")
        
        for model in vlm_models + ocr_models:
            model_key = model['name'].lower().replace('/', '_').replace('-', '_')
            if model_key not in current_models:
                print(f"   + {model['name']} ({model['size_gb']} GB)")
                print(f"     Suggested key: {model_key}")
        
        print()
    
    print("✅ Analysis complete!")

if __name__ == "__main__":
    main()