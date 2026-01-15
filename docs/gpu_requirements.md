# GPU Requirements and Compatibility

## VRAM Requirements by Model

| Model | Parameters | FP16/BF16 | INT8 | Recommended |
|-------|------------|-----------|------|-------------|
| GOT-OCR 2.0 | 580M | 3 GB | 2 GB | 4 GB |
| Qwen2-VL 2B | 2B | 4.7 GB | 3.6 GB | 6 GB |
| Qwen2-VL 7B | 7B | 16.1 GB | 10.1 GB | 12 GB |
| dots.ocr | 1.7B | 8 GB | 6 GB | 10 GB |

**Note**: Add 1-2 GB buffer for PyTorch overhead.

## RTX 50-Series Compatibility

### RTX 5090 (32GB)
✅ **All models** - Best choice for research

### RTX 5080 / 5070 Ti (16GB)  
✅ **Excellent** - All models except 7B@FP16
- dots.ocr + Qwen2-VL 7B (INT8) = ~18GB

### RTX 5070 (12GB)
⚠️ **Good** - Most models with optimization
- dots.ocr (BF16) + Qwen2-VL 2B (FP16) = 12.7GB (tight)
- Qwen2-VL 7B (INT8) = 10.1GB ✅

### RTX 5060 Ti 16GB
✅ **Best value** for document OCR
- All models except 7B@FP16
- Great for production

### RTX 5060 Ti / 5060 / 5050 (8GB)
⚠️ **Limited** - INT8 quantization required
- GOT-OCR (INT8) = 2GB ✅
- Qwen2-VL 2B (INT8) = 3.6GB ✅  
- dots.ocr (INT8) = 6GB ⚠️
- Qwen2-VL 7B = ❌

## RTX 40-Series

| GPU | VRAM | Status | Best For |
|-----|------|--------|----------|
| RTX 4090 | 24GB | ✅ Excellent | All models |
| RTX 4080 | 16GB | ✅ Excellent | All except 7B@FP16 |
| RTX 4070 Ti | 12GB | ⚠️ Good | 2B, dots.ocr, 7B@INT8 |
| RTX 4060 Ti | 16GB | ✅ Good | All except 7B@FP16 |
| RTX 4060 Ti | 8GB | ⚠️ Limited | INT8 only |

## RTX 30-Series

| GPU | VRAM | Status |
|-----|------|--------|
| RTX 3090 | 24GB | ✅ Excellent |
| RTX 3080 | 10/12GB | ⚠️ Moderate |
| RTX 3060 | 12GB | ⚠️ Good for 2B/dots.ocr |

## Checking Your GPU

```bash
python scripts/check_gpu.py
```

Output:
```
GPU: NVIDIA GeForce RTX 5070
VRAM: 12.00 GB

✅ GOT-OCR 2.0: Works with FP16
✅ Qwen2-VL 2B: Works with FP16
⚠️ Qwen2-VL 7B: Use INT8 instead
✅ dots.ocr: Works with BF16
```

## Optimization Tips

### For 8GB GPUs
```python
config = {
    "precision": "int8",
    "max_batch_size": 1,
    "optimize_memory": True
}
```

### For 12GB GPUs
```python
config = {
    "precision": "fp16",  # or bf16
    "use_flash_attention": True,
    "max_batch_size": 2
}
```

### For 16GB+ GPUs
```python
config = {
    "precision": "bf16",
    "use_flash_attention": True,
    "max_batch_size": 4
}
```

## Recommendations by VRAM

### 8 GB
- **Best setup**: GOT-OCR + Qwen2-VL 2B (INT8)
- Use INT8 quantization
- batch_size=1

### 12 GB  
- **Best setup**: dots.ocr (BF16) + Qwen2-VL 2B (FP16)
- Or Qwen2-VL 7B (INT8) alone
- Can run 2 models simultaneously

### 16 GB
- **Best setup**: All models (FP16/BF16)
- dots.ocr + Qwen2-VL 7B (INT8)
- Multiple simultaneous models

### 24 GB+
- **Best setup**: All models (FP16/BF16)
- Multiple simultaneous models
- Large batch sizes

## Buying Guide

| Budget | Recommendation | Why |
|--------|----------------|-----|
| <$500 | RTX 5060 Ti 16GB | Best value for OCR |
| $500-1000 | RTX 5070 (12GB) | Balanced performance |
| $1000-2000 | RTX 5080 (16GB) | Best all-around |
| $2000+ | RTX 5090 (32GB) | No limitations |

## Common Issues

### Out of Memory (OOM)
**Solutions**:
1. Lower precision (INT8)
2. Reduce batch_size to 1
3. Enable memory optimization
4. Close other GPU apps

### Slow Inference  
**Solutions**:
1. Enable Flash Attention
2. Use FP16/BF16 (not FP32)
3. Check GPU utilization
4. Update drivers

## Summary

For optimal **document OCR** experience:
- **Minimum**: 8GB (INT8)
- **Recommended**: 12GB (FP16/BF16)
- **Optimal**: 16GB+ (BF16, multiple models)

**Best value**: RTX 5060 Ti 16GB