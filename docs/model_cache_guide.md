# Model Cache Management Guide

## Overview

ChatVLMLLM uses HuggingFace's model caching system to efficiently store and reuse downloaded models. This guide explains how to manage the model cache.

## Cache Location

### Default Cache Directory

```
~/.cache/huggingface/hub/
```

**Linux/Mac**: `/home/username/.cache/huggingface/hub/`  
**Windows**: `C:\Users\username\.cache\huggingface\hub\`

### Custom Cache Directory

You can set a custom cache location using environment variables:

```bash
# In .env file or shell
export HF_HOME="/path/to/custom/cache"
# or
export HUGGINGFACE_HUB_CACHE="/path/to/custom/cache/hub"
```

## Checking Model Status

### Quick Check

```bash
python scripts/check_models.py
```

This script will show:
- ✅ Which models are configured
- ✅ Which models are in cache
- ✅ Cache size and locations
- ✅ Recommendations for next steps

### Programmatic Check

```python
from models.model_loader import ModelLoader

# Check if specific model is cached
is_cached, msg = ModelLoader.check_model_cache('got_ocr')
print(f"GOT-OCR cached: {is_cached}")
print(f"Status: {msg}")

# Get cache info
cache_info = ModelLoader.get_cache_info()
print(f"Total cached models: {cache_info['model_count']}")
print(f"Total size: {cache_info['total_size_gb']:.2f} GB")
```

## Model Download Behavior

### Automatic Download

Models are downloaded automatically when first used:

```python
from models import ModelLoader

# Will download if not cached
model = ModelLoader.load_model('got_ocr')
```

### Manual Pre-download

Download models before using the app:

```bash
# Interactive downloader
python scripts/download_models.py
```

Options:
- Download specific model by number
- Download all models at once
- Skip already cached models

## Cache Management

### View Cache Contents

```python
from utils.model_cache import ModelCacheManager

cache_manager = ModelCacheManager()
cached_models = cache_manager.list_cached_models()

for model in cached_models:
    print(f"{model['model_id']}: {model['size_gb']:.2f} GB")
```

### Delete Specific Model

```python
from utils.model_cache import ModelCacheManager

cache_manager = ModelCacheManager()
success = cache_manager.delete_model_cache('stepfun-ai/GOT-OCR2_0')

if success:
    print("Model deleted from cache")
```

### Clean All Cache

```bash
# Use cleanup script (careful - removes all app caches)
python scripts/cleanup.py
```

Or manually:

```bash
# Remove entire HuggingFace cache
rm -rf ~/.cache/huggingface/hub/

# Models will re-download on next use
```

## Model Sizes

### Expected Cache Sizes

| Model | Size | VRAM | Precision |
|-------|------|------|----------|
| GOT-OCR 2.0 | ~2-3 GB | ~3 GB | FP16 |
| Qwen2-VL 2B | ~4-5 GB | ~5 GB | FP16 |
| Qwen2-VL 7B | ~14-15 GB | ~14 GB | FP16 |

### Disk Space Planning

- **Minimal setup** (GOT-OCR only): ~3 GB
- **Standard setup** (GOT-OCR + Qwen2-VL 2B): ~8 GB
- **Full setup** (all models): ~22 GB

**Recommendation**: Keep at least 30 GB free for comfortable operation.

## Sharing Cache

### Between Projects

HuggingFace cache is shared across all projects automatically. If you use the same models in multiple projects, they'll reuse the same cache.

### Between Users

On shared systems:

```bash
# Set shared cache location
export HF_HOME="/shared/huggingface/cache"

# Ensure permissions
chmod -R 755 /shared/huggingface/cache
```

## Troubleshooting

### Model Not Found

**Problem**: Model shows as "not cached" even after download.

**Solutions**:
1. Check cache location: `echo $HF_HOME`
2. Verify download completed: `python scripts/check_models.py`
3. Check disk space: `df -h ~/.cache`
4. Re-download: Delete cache and try again

### Corrupted Cache

**Problem**: Model fails to load with cache errors.

**Solutions**:

```bash
# Delete specific model
rm -rf ~/.cache/huggingface/hub/models--stepfun-ai--GOT-OCR2_0

# Re-download
python scripts/download_models.py
```

### Disk Space Issues

**Problem**: Running out of disk space.

**Solutions**:

1. **Remove unused models**:
```python
from utils.model_cache import ModelCacheManager

cache_manager = ModelCacheManager()
for model in cache_manager.list_cached_models():
    print(f"{model['model_id']}: {model['size_gb']} GB")
    # Delete if not needed
    # cache_manager.delete_model_cache(model['model_id'])
```

2. **Move cache to larger drive**:
```bash
# Move cache
mv ~/.cache/huggingface /mnt/large_drive/huggingface

# Create symlink
ln -s /mnt/large_drive/huggingface ~/.cache/huggingface
```

3. **Use quantized models** (smaller but may affect quality):
```yaml
# In config.yaml
models:
  qwen_vl_2b:
    precision: "int8"  # Instead of fp16
```

## Best Practices

### ✅ Do

- Pre-download models before presentations/demos
- Check cache status regularly
- Keep at least 10 GB free space
- Use `check_models.py` before running app
- Share cache between projects

### ❌ Don't

- Delete cache while models are loading
- Manually edit cache files
- Store cache on slow drives (affects performance)
- Share cache across different Python environments without testing

## Cache Performance

### First Load (Download)

```
GOT-OCR 2.0:    ~10-15 minutes (depends on internet speed)
Qwen2-VL 2B:    ~15-20 minutes
Qwen2-VL 7B:    ~30-45 minutes
```

### Subsequent Loads (From Cache)

```
GOT-OCR 2.0:    ~10-30 seconds
Qwen2-VL 2B:    ~15-45 seconds
Qwen2-VL 7B:    ~30-90 seconds
```

**Note**: Load times depend on:
- Storage speed (SSD vs HDD)
- Available RAM
- GPU initialization
- Model precision

## Advanced: Cache Optimization

### Symbolic Links for Organization

```bash
# Create organized cache structure
mkdir -p /data/models/got-ocr
mkdir -p /data/models/qwen-vl

# Move models
mv ~/.cache/huggingface/hub/models--stepfun-ai--GOT-OCR2_0 /data/models/got-ocr/
mv ~/.cache/huggingface/hub/models--Qwen--Qwen2-VL-2B-Instruct /data/models/qwen-vl/

# Create symlinks
ln -s /data/models/got-ocr/models--stepfun-ai--GOT-OCR2_0 ~/.cache/huggingface/hub/
ln -s /data/models/qwen-vl/models--Qwen--Qwen2-VL-2B-Instruct ~/.cache/huggingface/hub/
```

### Backup Cache

```bash
# Backup to archive
tar -czf huggingface_cache_backup.tar.gz ~/.cache/huggingface/

# Restore from archive
tar -xzf huggingface_cache_backup.tar.gz -C ~/
```

## Monitoring Cache

### Create Monitoring Script

```python
# scripts/monitor_cache.py
from utils.model_cache import ModelCacheManager
import time

def monitor():
    cache_manager = ModelCacheManager()
    
    while True:
        info = cache_manager.get_cache_info()
        print(f"\rCached: {info['model_count']} models, "
              f"{info['total_size_gb']:.2f} GB", end='')
        time.sleep(5)

if __name__ == "__main__":
    monitor()
```

## Summary

- ✅ Cache is automatic and efficient
- ✅ Use `check_models.py` to verify status
- ✅ Models download once, reuse forever
- ✅ Can be shared across projects
- ✅ Easy to manage and clean

For issues, see [Troubleshooting](#troubleshooting) section.