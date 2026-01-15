#!/usr/bin/env python3
"""GPU compatibility checker for ChatVLMLLM models."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import yaml


def get_gpu_info():
    """Get GPU information."""
    try:
        import torch
        if not torch.cuda.is_available():
            return None
        return {
            "name": torch.cuda.get_device_name(0),
            "vram_gb": round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2),
            "cuda_version": torch.version.cuda
        }
    except:
        return None


def get_vram_requirements():
    """Get VRAM requirements per model."""
    return {
        "got_ocr": {"fp16": 3.0, "int8": 2.0, "min": 4.0},
        "qwen_vl_2b": {"fp16": 4.7, "bf16": 4.7, "int8": 3.6, "min": 6.0},
        "qwen_vl_7b": {"fp16": 16.1, "bf16": 16.1, "int8": 10.1, "min": 12.0},
        "dots_ocr": {"fp16": 8.0, "bf16": 8.0, "int8": 6.0, "min": 8.0}
    }


def check_compatibility(vram_gb, model_key, precision):
    """Check model compatibility."""
    reqs = get_vram_requirements()
    if model_key not in reqs:
        return None, None, "Unknown model"
    
    req = reqs[model_key]
    vram_needed = req.get(precision, req.get("fp16", 0))
    vram_with_buffer = vram_needed + 1.0
    
    if vram_gb >= vram_with_buffer:
        return "✅", vram_needed, f"Works with {precision.upper()}"
    elif vram_gb >= vram_needed:
        return "⚠️", vram_needed, "Tight fit, no buffer"
    else:
        # Find compatible precision
        for prec in ["int8", "fp16", "bf16"]:
            if prec in req and req[prec] + 1.0 <= vram_gb:
                return "⚠️", req[prec], f"Use {prec.upper()} instead"
        return "❌", vram_needed, f"Need {req['min']:.1f}GB minimum"


def main():
    print("\n" + "="*60)
    print("ChatVLMLLM GPU Compatibility Checker")
    print("="*60 + "\n")
    
    gpu = get_gpu_info()
    if not gpu:
        print("❌ No GPU detected\n")
        return 1
    
    print(f"GPU: {gpu['name']}")
    print(f"VRAM: {gpu['vram_gb']:.2f} GB")
    print(f"CUDA: {gpu['cuda_version']}\n")
    
    config_path = project_root / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    print("="*60)
    print("Model Compatibility")
    print("="*60 + "\n")
    
    for key, cfg in config["models"].items():
        precision = cfg.get('precision', 'fp16')
        status, vram, msg = check_compatibility(gpu['vram_gb'], key, precision)
        
        print(f"🤖 {cfg['name']}")
        print(f"   Precision: {precision.upper()}")
        print(f"   Required: {vram:.1f} GB (+1GB buffer)")
        print(f"   Status: {status} {msg}\n")
    
    print("="*60)
    print("Recommendations")
    print("="*60 + "\n")
    
    if gpu['vram_gb'] >= 16:
        print("✅ Excellent! Can run all models.")
    elif gpu['vram_gb'] >= 12:
        print("✅ Good! Run most models with FP16/INT8.")
        print("   Best: dots.ocr + Qwen2-VL 2B")
    elif gpu['vram_gb'] >= 8:
        print("⚠️  Limited. Use INT8 quantization.")
        print("   Best: GOT-OCR + Qwen2-VL 2B (INT8)")
    else:
        print("❌ Insufficient VRAM for most models.")
    
    print("\n💡 Tips:")
    print("  - Close other GPU applications")
    print("  - Use INT8 for lower memory")
    print("  - batch_size=1 for tight VRAM")
    print("\n" + "="*60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())