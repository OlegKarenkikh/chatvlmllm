# ChatVLMLLM - Document OCR & Vision-Language Models

A comprehensive toolkit for document OCR, visual understanding, and multimodal AI applications using state-of-the-art vision-language models.

## ✨ Features

### Supported Models

- 🔍 **GOT-OCR 2.0** - Specialized OCR for complex layouts
- 🤖 **Qwen2-VL** (2B, 7B) - Advanced vision-language understanding
- ⭐ **Qwen3-VL** (2B, 4B, 8B) - Latest VLM with 32 languages OCR, visual agent, 256K context
- 📚 **dots.ocr** - SOTA multilingual document parser (100+ languages)

### Key Capabilities

- 🌐 **Multilingual OCR** - 32+ languages with high accuracy
- 🤖 **Visual Agent** - GUI interaction and automation (Qwen3-VL)
- 📊 **Document Analysis** - Layout detection, table extraction, structure parsing
- 🧠 **Visual Reasoning** - Complex reasoning about images and diagrams
- 🎥 **Video Understanding** - 256K context for long videos (Qwen3-VL)
- 📦 **Flexible Quantization** - FP16, INT8, INT4 support
- ⚡ **Flash Attention 2** - Faster inference with lower memory

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/OlegKarenkikh/chatvlmllm.git
cd chatvlmllm

# Install dependencies
pip install -r requirements.txt

# Install latest transformers for Qwen3-VL
pip install git+https://github.com/huggingface/transformers
```

### Check GPU Compatibility

```bash
python scripts/check_gpu.py
```

### Basic Usage

```python
from models import ModelLoader
from PIL import Image

# Load Qwen3-VL 2B
model = ModelLoader.load_model('qwen3_vl_2b')

# Process image
image = Image.open('document.jpg')
result = model.chat(
    image=image,
    prompt="Extract all text from this document"
)

print(result)
```

### Streamlit App

```bash
streamlit run app.py
```

## 📊 GPU Requirements

| GPU | VRAM | Best Model | Status |
|-----|------|-----------|--------|
| RTX 5090 | 32GB | Qwen3-VL 8B@FP16 | ✅ Perfect |
| RTX 5080 | 16GB | Qwen3-VL 8B@INT8 | ✅ Excellent |
| RTX 5070 | 12GB | Qwen3-VL 4B@FP16 | ✅ Good |
| RTX 5060 Ti | 16GB | Qwen3-VL 8B@INT8 | ✅ Best Value |
| RTX 5060 Ti | 8GB | Qwen3-VL 4B@INT4 | ⚠️ Limited |

See [GPU Requirements Guide](docs/gpu_requirements.md) for detailed compatibility.

## 📖 Documentation

- [GPU Requirements](docs/gpu_requirements.md) - Comprehensive GPU compatibility guide
- [Qwen3-VL Guide](docs/qwen3_vl_guide.md) - Qwen3-VL usage and optimization
- [Model Cache Guide](docs/model_cache_guide.md) - Managing model downloads

## 🛠️ Configuration

### config.yaml

```yaml
models:
  qwen3_vl_8b:
    model_path: "Qwen/Qwen3-VL-8B-Instruct"
    precision: "int8"  # fp16, bf16, int8, int4
    use_flash_attention: true
    device_map: "auto"
```

### INT4 Quantization (66% VRAM Reduction)

```yaml
models:
  qwen3_vl_8b:
    precision: "int4"  # 17.6GB -> 6GB
```

## ✨ What's New

### Qwen3-VL (Latest)

- 🌐 **32 languages OCR** (vs 19 in Qwen2-VL)
- 🤖 **Visual agent** capabilities
- 📚 **256K context** (expandable to 1M)
- 🎯 **3D grounding** for spatial reasoning
- 🧠 **Thinking mode** for complex tasks
- 📦 **INT4 support** - 66% less VRAM

## 💻 Usage Examples

### Document OCR

```python
# Extract text from document
text = model.extract_text(image, language="Russian")
```

### Document Analysis

```python
# Analyze document structure
analysis = model.analyze_document(image, focus="layout")
```

### Visual Reasoning

```python
# Complex reasoning
reasoning = model.visual_reasoning(
    image, 
    question="Explain the workflow in this diagram"
)
```

### Visual Agent (Qwen3-VL)

```python
# GUI interaction
actions = model.chat(
    image=screenshot,
    prompt="Find and click the Submit button"
)
```

## 💡 Tips & Best Practices

### For 8GB VRAM

```python
# Use INT4 quantization
model = ModelLoader.load_model(
    'qwen3_vl_8b',
    precision='int4'  # 6GB instead of 17.6GB
)
```

### For 12GB VRAM

```python
# Run multiple models
qwen4b = ModelLoader.load_model('qwen3_vl_4b')  # 8.9GB
qwen2b = ModelLoader.load_model('qwen3_vl_2b')  # 4.4GB
# Total: 11.1GB with INT8
```

### For 16GB+ VRAM

```python
# Optimal quality
model = ModelLoader.load_model(
    'qwen3_vl_8b',
    precision='int8',  # 10GB
    use_flash_attention=True
)
```

## 🔧 Development

### Project Structure

```
chatvlmllm/
├── models/
│   ├── got_ocr.py          # GOT-OCR integration
│   ├── qwen_vl.py          # Qwen2-VL integration
│   ├── qwen3_vl.py         # Qwen3-VL integration
│   ├── dots_ocr.py         # dots.ocr integration
│   └── model_loader.py     # Model factory
├── utils/
│   ├── logger.py
│   └── model_cache.py
├── scripts/
│   ├── check_gpu.py        # GPU compatibility checker
│   └── check_models.py     # Model cache checker
├── docs/
│   ├── gpu_requirements.md
│   └── qwen3_vl_guide.md
├── app.py                  # Streamlit app
└── config.yaml             # Configuration
```

### Testing

```bash
pytest tests/
```

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📝 License

MIT License

## 🔗 Links

- **Qwen3-VL**: https://github.com/QwenLM/Qwen3-VL
- **GOT-OCR**: https://github.com/Ucas-HaoranWei/GOT-OCR2.0
- **dots.ocr**: https://github.com/rednote-hilab/dots.ocr

## ⭐ Acknowledgments

- Qwen Team for Qwen3-VL
- Stepfun AI for GOT-OCR 2.0
- RedNote for dots.ocr

---

**Star ⭐ this repo if you find it useful!**