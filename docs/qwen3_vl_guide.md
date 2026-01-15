# Qwen3-VL Integration Guide

## Overview

Qwen3-VL represents the latest advancement in vision-language models from the Qwen family, released in late 2025.

### Key Improvements over Qwen2-VL

- 🌐 **32 languages OCR** (up from 19)
- 🤖 **Visual agent capabilities** - GUI interaction
- 📚 **256K context** (expandable to 1M)
- 🎯 **Enhanced spatial perception** with 3D grounding
- 🎥 **Advanced video understanding**
- 🧠 **Thinking mode** for complex reasoning
- 📦 **INT4 quantization support**

## Available Models

| Model | Parameters | Type | Best For |
|-------|------------|------|----------|
| Qwen3-VL-2B | 2B | Dense | Fast inference, low VRAM |
| Qwen3-VL-4B | 4B | Dense | Balanced performance |
| Qwen3-VL-8B | 8B | Dense | Maximum quality |
| Qwen3-VL-30B | 30B | MoE | API/cloud only |
| Qwen3-VL-235B | 235B | MoE | API/cloud only |

## VRAM Requirements

### Qwen3-VL-2B
- **FP16**: 4.4 GB
- **INT8**: 2.2 GB
- **Recommended**: 6 GB

### Qwen3-VL-4B
- **FP16**: 8.9 GB
- **INT8**: 3.8 GB
- **INT4**: 3 GB
- **Recommended**: 10 GB

### Qwen3-VL-8B
- **FP16**: 17.6 GB
- **INT8**: 10 GB
- **INT4**: 6 GB
- **Recommended**: 18 GB

## Usage Examples

### Basic Image Analysis

```python
from models import ModelLoader
from PIL import Image

# Load model
model = ModelLoader.load_model('qwen3_vl_2b')

# Process image
image = Image.open('document.jpg')
response = model.chat(
    image=image,
    prompt="Describe this image in detail."
)

print(response)
```

### Enhanced OCR (32 Languages)

```python
# Extract text with language hint
text = model.extract_text(
    image=image,
    language="Russian"  # Supports 32 languages
)

print(text)
```

### Document Analysis

```python
# Analyze document structure
analysis = model.analyze_document(
    image=image,
    focus="layout"  # or 'content', 'tables'
)

print(analysis)
```

### Visual Reasoning

```python
# Complex reasoning task
reasoning = model.visual_reasoning(
    image=image,
    question="Why is this design effective?"
)

print(reasoning)
```

## INT4 Quantization

### Configuration

```yaml
# config.yaml
models:
  qwen3_vl_8b:
    precision: "int4"
    use_flash_attention: true
```

### Manual Setup

```python
from transformers import BitsAndBytesConfig
import torch

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

model = Qwen3VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen3-VL-8B-Instruct",
    quantization_config=quant_config,
    device_map="auto"
)
```

### Memory Savings

- **8B FP16**: 17.6 GB → **INT4**: 6 GB = **66% reduction**
- **4B FP16**: 8.9 GB → **INT4**: 3 GB = **66% reduction**

## Performance Tips

### Enable Flash Attention 2

```python
model = ModelLoader.load_model(
    'qwen3_vl_8b',
    use_flash_attention=True
)
```

**Benefits**:
- 30-50% faster inference
- Lower memory usage
- Better for long contexts

### Batch Processing

```python
images = [Image.open(f"doc{i}.jpg") for i in range(4)]

results = []
for img in images:
    result = model.process_image(img, prompt="Extract text")
    results.append(result)
```

### Optimal Settings by VRAM

#### 8 GB
```yaml
qwen3_vl_4b:
  precision: "int4"
  max_batch_size: 1
  use_flash_attention: true
```

#### 12 GB
```yaml
qwen3_vl_4b:
  precision: "fp16"
  max_batch_size: 2
  use_flash_attention: true
```

#### 16 GB
```yaml
qwen3_vl_8b:
  precision: "int8"
  max_batch_size: 2
  use_flash_attention: true
```

## Comparison with Other Models

### vs Qwen2-VL

| Feature | Qwen2-VL 7B | Qwen3-VL 8B |
|---------|-------------|-------------|
| Parameters | 7B | 8B |
| OCR Languages | 19 | **32** |
| Context | 32K | **256K-1M** |
| Visual Agent | ❌ | **✅** |
| 3D Grounding | ❌ | **✅** |
| INT4 Support | ❌ | **✅** |
| VRAM (INT8) | 10.1 GB | 10 GB |

### vs dots.ocr

| Feature | dots.ocr | Qwen3-VL 4B |
|---------|----------|-------------|
| Parameters | 1.7B | 4B |
| Languages | 100+ | 32 |
| Layout | ✅ Advanced | ✅ Good |
| Reasoning | ❌ | ✅ **Advanced** |
| Agent | ❌ | ✅ **Yes** |
| VRAM (FP16) | 8 GB | 8.9 GB |

**Recommendation**: 
- Use **dots.ocr** for pure document parsing
- Use **Qwen3-VL** for reasoning + OCR

## Troubleshooting

### ImportError: Qwen3VLForConditionalGeneration

```bash
pip install git+https://github.com/huggingface/transformers
# or wait for transformers>=4.57.0
```

### Out of Memory

1. **Use INT4**: `precision: "int4"`
2. **Reduce batch**: `max_batch_size: 1`
3. **Close apps**: Check `nvidia-smi`
4. **Use smaller model**: Switch to 4B or 2B

### Slow Inference

1. **Flash Attention**: `use_flash_attention: true`
2. **Check dtype**: Use FP16/BF16, not FP32
3. **Update drivers**: Latest CUDA
4. **Check load**: `nvidia-smi dmon`

## Best Practices

### For Document OCR

```python
# Use with language hint for better accuracy
text = model.extract_text(
    image=document,
    language="English"  # or Russian, Chinese, etc.
)
```

### For Visual Reasoning

```python
# Enable thinking mode for complex questions
response = model.visual_reasoning(
    image=diagram,
    question="Explain the workflow step by step"
)
```

### For Batch Processing

```python
# Process multiple documents efficiently
for batch in batches(documents, size=4):
    results = process_batch(batch)
```

## Resources

- **Official Repo**: https://github.com/QwenLM/Qwen3-VL
- **HuggingFace**: https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct
- **Paper**: https://arxiv.org/abs/2505.09388
- **Blog**: https://qwen.ai/blog