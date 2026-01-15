# GPU Requirements and Compatibility

## VRAM Requirements by Model

| Model | Parameters | FP16/BF16 | INT8 | INT4 | Recommended |
|-------|------------|-----------|------|------|-------------|
| GOT-OCR 2.0 | 580M | 3 GB | 2 GB | - | 4 GB |
| Qwen2-VL 2B | 2B | 4.7 GB | 3.6 GB | - | 6 GB |
| Qwen2-VL 7B | 7B | 16.1 GB | 10.1 GB | - | 12 GB |
| **Qwen3-VL 2B** | **2B** | **4.4 GB** | **2.2 GB** | - | **6 GB** |
| **Qwen3-VL 4B** | **4B** | **8.9 GB** | **3.8 GB** | **3 GB** | **10 GB** |
| **Qwen3-VL 8B** | **8B** | **17.6 GB** | **10 GB** | **6 GB** | **18 GB** |
| dots.ocr | 1.7B | 8 GB | 6 GB | - | 10 GB |

**Note**: Add 1-2 GB buffer for PyTorch overhead.

## Qwen3-VL Highlights (NEW)

🌐 **32 languages OCR** | 🤖 **Visual agent** | 📚 **256K context** | 🎯 **3D grounding** | 🧠 **Thinking mode** | 📦 **INT4 support**

See [Qwen3-VL Guide](qwen3_vl_guide.md) for detailed usage.

## RTX 50-Series Compatibility

### RTX 5090 (32GB)
✅ **All models** - Best choice for research

### RTX 5080 / 5070 Ti (16GB)  
✅ **Excellent** - All models except 8B@FP16 and 7B@FP16
- **Qwen3-VL 8B (INT8)** = 10GB ✅
- Qwen3-VL 4B + dots.ocr = 14.9GB ✅
- dots.ocr + Qwen2-VL 7B (INT8) = ~18GB

### RTX 5070 (12GB)
⚠️ **Good** - Most models with optimization
- **Qwen3-VL 8B (INT4)** + GOT-OCR = 9GB ✅
- **Qwen3-VL 4B (FP16)** = 8.9GB ✅
- dots.ocr (BF16) + Qwen2-VL 2B (FP16) = 12.7GB (tight)
- Qwen2-VL 7B (INT8) = 10.1GB ✅

### RTX 5060 Ti 16GB
✅ **Best value** for document OCR
- **Qwen3-VL 8B (INT8)** = 10GB ✅
- Qwen3-VL 4B + dots.ocr = 16.9GB ⚠️
- All models except 8B@FP16 and 7B@FP16
- Great for production

### RTX 5060 Ti / 5060 / 5050 (8GB)
⚠️ **Limited** - INT8/INT4 quantization required
- **Qwen3-VL 4B (INT4)** = 3GB ✅
- **Qwen3-VL 2B (FP16)** = 4.4GB ✅
- GOT-OCR (INT8) = 2GB ✅
- Qwen2-VL 2B (INT8) = 3.6GB ✅  
- dots.ocr (INT8) = 6GB ⚠️
- Qwen2-VL 7B = ❌

## RTX 40-Series

| GPU | VRAM | Status | Best For |
|-----|------|--------|----------|
| RTX 4090 | 24GB | ✅ Excellent | Qwen3-VL 8B@FP16 |
| RTX 4080 | 16GB | ✅ Excellent | Qwen3-VL 8B@INT8 |
| RTX 4070 Ti | 12GB | ⚠️ Good | Qwen3-VL 4B@FP16 |
| RTX 4060 Ti | 16GB | ✅ Good | Qwen3-VL 8B@INT8 |
| RTX 4060 Ti | 8GB | ⚠️ Limited | Qwen3-VL 4B@INT4 |

## RTX 30-Series

| GPU | VRAM | Status |
|-----|------|--------|
| RTX 3090 | 24GB | ✅ Excellent |
| RTX 3080 | 10/12GB | ⚠️ Moderate |
| RTX 3060 | 12GB | ⚠️ Good for 2B/4B |

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
✅ Qwen3-VL 2B: Works with FP16
✅ Qwen3-VL 4B: Works with FP16
⚠️ Qwen3-VL 8B: Use INT4 instead
⚠️ Qwen2-VL 7B: Use INT8 instead
✅ dots.ocr: Works with BF16
```

## Optimization Tips

### For 8GB GPUs
```python
config = {
    "precision": "int4",  # Qwen3-VL only
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
- **Best setup**: Qwen3-VL 4B (INT4) + GOT-OCR = 5GB
- **Alternative**: Qwen3-VL 2B (FP16) + GOT-OCR = 6.4GB
- Use INT8/INT4 quantization
- batch_size=1

### 12 GB  
- **Best setup**: Qwen3-VL 4B (FP16) + Qwen3-VL 2B (INT8) = 11.1GB
- **Alternative**: Qwen3-VL 8B (INT4) + GOT-OCR = 9GB
- Or dots.ocr (BF16) + Qwen2-VL 2B (FP16) = 12.7GB
- Can run 2-3 models simultaneously

### 16 GB
- **Best setup**: Qwen3-VL 8B (INT8) + Qwen3-VL 2B = 14.4GB
- **Alternative**: Qwen3-VL 4B + dots.ocr = 16.9GB
- All models except 8B@FP16 and 7B@FP16
- Multiple simultaneous models

### 18+ GB
- **Best setup**: Qwen3-VL 8B (FP16) = 17.6GB
- All models at optimal precision
- Multiple simultaneous models

### 24 GB+
- **Best setup**: All models (FP16/BF16)
- Multiple simultaneous models
- Large batch sizes

## Model Comparison

### Qwen3-VL vs Qwen2-VL

| Feature | Qwen2-VL | Qwen3-VL |
|---------|----------|----------|
| OCR Languages | 19 | **32** |
| Context Length | 32K | **256K-1M** |
| Visual Agent | ❌ | **✅** |
| 3D Grounding | ❌ | **✅** |
| Thinking Mode | ❌ | **✅** |
| INT4 Support | ❌ | **✅** |
| VRAM (2B, FP16) | 4.7GB | **4.4GB** |

⭐ **Recommendation**: Qwen3-VL offers better capabilities with same or lower VRAM.

## Buying Guide 2026

| Budget | Recommendation | VRAM | Why |
|--------|----------------|------|-----|
| <$500 | RTX 5060 Ti | 16GB | Best value, runs Qwen3-VL 8B (INT8) |
| $500-1000 | RTX 5070 | 12GB | Balanced, Qwen3-VL 4B@FP16 |
| $1000-2000 | RTX 5080 | 16GB | Best all-around |
| $2000+ | RTX 5090 | 32GB | No limitations |

**Best value 2026**: RTX 5060 Ti 16GB

## Common Issues

### Out of Memory (OOM)
**Solutions**:
1. Use INT4 quantization (Qwen3-VL): `precision: "int4"`
2. Lower to INT8: `precision: "int8"`
3. Reduce batch_size to 1
4. Enable memory optimization
5. Close other GPU apps

### Slow Inference  
**Solutions**:
1. Enable Flash Attention 2
2. Use FP16/BF16 (not FP32)
3. Check GPU utilization (`nvidia-smi`)
4. Update drivers

### INT4 Quantization (Qwen3-VL)
```yaml
# config.yaml
models:
  qwen3_vl_8b:
    precision: "int4"
```

**VRAM savings**: 8B FP16 (17.6GB) → INT4 (6GB) = **66% reduction**

## Summary

For optimal **document OCR & VLM** experience:

### By Use Case

**Document OCR**:
- **Minimum**: 8GB (Qwen3-VL 2B + GOT-OCR)
- **Recommended**: 12GB (Qwen3-VL 4B + dots.ocr)
- **Optimal**: 16GB (Qwen3-VL 8B INT8)

**Visual Reasoning**:
- **Minimum**: 10GB (Qwen3-VL 4B FP16)
- **Recommended**: 16GB (Qwen3-VL 8B INT8)
- **Optimal**: 18GB (Qwen3-VL 8B FP16)

**Production**:
- **Small**: RTX 5060 Ti 16GB
- **Medium**: RTX 5080 16GB
- **Large**: RTX 5090 32GB

**Best overall value**: RTX 5060 Ti 16GB - runs Qwen3-VL 8B (INT8) perfectly.

---

📖 **See also**: [Qwen3-VL Usage Guide](qwen3_vl_guide.md) for detailed examples and best practices.