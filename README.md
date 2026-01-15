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
- 🚀 **REST API** - Production-ready FastAPI endpoints
- 🐳 **Docker Support** - GPU-enabled containerization

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

#### Python API

```python
from models import ModelLoader
from PIL import Image

# Load Qwen3-VL 2B
model = ModelLoader.load_model('qwen3_vl_2b')

# Process image
image = Image.open('document.jpg')
result = model.extract_text(image)

print(result)
```

#### Streamlit App

```bash
streamlit run app.py
```

Access: http://localhost:8501

#### REST API

```bash
# Start API server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Use API
curl -X POST "http://localhost:8000/ocr?model=qwen3_vl_2b" \
  -F "file=@document.jpg"
```

API Docs: http://localhost:8000/docs

#### Docker

```bash
# Build and run
docker-compose up -d

# Access services
# Streamlit: http://localhost:8501
# API: http://localhost:8000/docs
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
- [API Guide](docs/api_guide.md) - REST API documentation
- [Model Cache Guide](docs/model_cache_guide.md) - Managing model downloads

## 🔧 API Usage

### Python Client

```python
import requests

# OCR
with open('document.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/ocr',
        files={'file': f},
        params={'model': 'qwen3_vl_2b'}
    )
    print(response.json()['text'])

# Chat
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/chat',
        files={'file': f},
        data={'prompt': 'What\'s in this image?'}
    )
    print(response.json()['response'])
```

See [examples/api_usage.py](examples/api_usage.py) for more examples.

### cURL

```bash
# Health check
curl http://localhost:8000/health

# OCR
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@document.jpg" \
  -F "model=qwen3_vl_2b"

# Chat
curl -X POST "http://localhost:8000/chat" \
  -F "file=@image.jpg" \
  -F "prompt=Describe this image"
```

See [examples/api_curl.sh](examples/api_curl.sh) for more examples.

## 🐳 Docker Deployment

### Using docker-compose

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services

- **API**: http://localhost:8000
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc
- **Streamlit**: http://localhost:8501

### Requirements

- Docker 20.10+
- NVIDIA Docker runtime
- 16GB+ VRAM recommended

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

### v1.0.0 (2026-01-15)

#### 🎉 Major Features

- ✅ **Qwen3-VL Support** - All three models (2B, 4B, 8B)
- ✅ **REST API** - Production-ready FastAPI
- ✅ **Docker** - Full containerization with GPU support
- ✅ **Streamlit App** - Updated with all models
- ✅ **Documentation** - Complete API and usage guides

#### 🔥 Qwen3-VL Highlights

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
# Total: ~11GB with INT8
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
├── api.py                  # FastAPI REST API
├── app.py                  # Streamlit application
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
│   ├── qwen3_vl_guide.md
│   └── api_guide.md
├── examples/
│   ├── api_usage.py
│   └── api_curl.sh
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker services
└── config.yaml             # Configuration
```

### Testing

```bash
pytest tests/
```

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License

## 🔗 Links

- **GitHub**: https://github.com/OlegKarenkikh/chatvlmllm
- **Qwen3-VL**: https://github.com/QwenLM/Qwen3-VL
- **GOT-OCR**: https://github.com/Ucas-HaoranWei/GOT-OCR2.0
- **dots.ocr**: https://github.com/rednote-hilab/dots.ocr

## ⭐ Acknowledgments

- Qwen Team for Qwen3-VL
- Stepfun AI for GOT-OCR 2.0
- RedNote for dots.ocr

---

**Star ⭐ this repo if you find it useful!**

## 📊 Status

![GitHub stars](https://img.shields.io/github/stars/OlegKarenkikh/chatvlmllm?style=social)
![GitHub forks](https://img.shields.io/github/forks/OlegKarenkikh/chatvlmllm?style=social)
![License](https://img.shields.io/github/license/OlegKarenkikh/chatvlmllm)

**Production Ready** | **7 Models** | **REST API** | **Docker Support**