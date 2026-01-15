# ChatVLMLLM - Document OCR & Vision Language Models

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive educational research project exploring **Vision Language Models (VLM)** for document OCR tasks. This project provides a production-ready implementation with modern UI, comparing different model architectures and their performance on real-world document processing.

<p align="center">
  <img src="https://img.icons8.com/fluency/96/000000/artificial-intelligence.png" width="100"/>
</p>

## 🎯 Project Goals

This educational project aims to:

1. 🔬 **Research** - Compare specialized OCR models vs. general VLM models
2. 📊 **Benchmark** - Measure accuracy, speed, and resource usage
3. 🛠️ **Develop** - Build production-quality document processing application
4. 📚 **Learn** - Understand VLM architectures and their applications
5. 🌐 **Share** - Provide open-source implementation for community

## ✨ Features

### 🤖 Model Support

- **GOT-OCR 2.0** - Specialized OCR for complex layouts
- **Qwen2-VL 2B** - Lightweight vision-language model
- **Qwen2-VL 7B** - Advanced multimodal understanding

### 📄 Processing Modes

- **OCR Mode** - Extract text and structured data from documents
- **Chat Mode** - Interactive Q&A about document content
- **Batch Processing** - Process multiple documents efficiently
- **Comparison** - Side-by-side model performance analysis

### 💎 Production Features

- ✅ Modern Streamlit UI with custom styling
- ✅ HuggingFace model cache management
- ✅ Automatic model detection and download
- ✅ Export results (JSON, CSV, TXT)
- ✅ Input validation and error handling
- ✅ Comprehensive logging system
- ✅ Docker containerization
- ✅ Jupyter notebooks for exploration

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- CUDA-capable GPU (recommended, 6GB+ VRAM)
- 30GB+ free disk space (for models)

### Installation

```bash
# Clone repository
git clone https://github.com/OlegKarenkikh/chatvlmllm.git
cd chatvlmllm

# Automated setup
bash scripts/setup.sh  # Linux/Mac
# or
scripts\setup.bat      # Windows
```

### Check Environment

```bash
# Verify installation
python scripts/check_setup.py

# Check model cache status
python scripts/check_models.py
```

### Download Models (Optional)

Models download automatically on first use, but you can pre-download:

```bash
python scripts/download_models.py
```

### Run Application

```bash
streamlit run app.py
```

Open browser to: http://localhost:8501

## 📖 Documentation

### Core Documentation

- [**Quick Start Guide**](QUICKSTART.md) - Get started in 5 minutes
- [**Model Documentation**](docs/models.md) - Detailed model information
- [**Architecture Overview**](docs/architecture.md) - System design
- [**Developer Guide**](README_DEV.md) - Development setup and workflow
- [**Model Cache Guide**](docs/model_cache_guide.md) - Cache management

### Additional Resources

- [Research Log Template](docs/research_log.md) - Track your experiments
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- [Project Summary](PROJECT_SUMMARY.md) - Complete project overview
- [Changelog](CHANGELOG.md) - Version history

## 🎓 Using the Project

### For Students

1. **Explore Models**
   ```bash
   jupyter notebook notebooks/01_model_exploration.ipynb
   ```

2. **Run Experiments**
   - Process test documents
   - Compare model outputs
   - Measure performance metrics

3. **Document Results**
   - Fill in [research_log.md](docs/research_log.md)
   - Create comparison charts
   - Write analysis report

### For Developers

1. **Extend Functionality**
   ```python
   # Add custom model
   from models.base_model import BaseModel
   
   class MyModel(BaseModel):
       def load_model(self):
           # Your implementation
           pass
   ```

2. **Run Tests**
   ```bash
   pytest
   pytest --cov=models --cov=utils
   ```

3. **Deploy**
   ```bash
   docker-compose -f docker/docker-compose.yml up
   ```

## 🔧 Model Cache Management

### Check Cache Status

```bash
python scripts/check_models.py
```

Output example:
```
✅ GOT-OCR 2.0: Found in cache (2.8 GB)
⚠️  Qwen2-VL 2B: Not cached - will download on first use
✅ Qwen2-VL 7B: Found in cache (14.2 GB)

Total: 2 models, 17.0 GB
```

### Cache Location

Default: `~/.cache/huggingface/hub/`

Custom location:
```bash
export HF_HOME="/path/to/cache"
```

See [Model Cache Guide](docs/model_cache_guide.md) for details.

## 📊 Model Comparison

| Model | Parameters | VRAM | Speed | Best For |
|-------|-----------|------|-------|----------|
| GOT-OCR 2.0 | 580M | ~3GB | Fast | Complex layouts, tables, formulas |
| Qwen2-VL 2B | 2B | ~5GB | Fast | General OCR, lightweight deployment |
| Qwen2-VL 7B | 7B | ~14GB | Medium | Advanced analysis, reasoning |

## 🛠️ Development

### Project Structure

```
chatvlmllm/
├── app.py                 # Streamlit application
├── config.yaml           # Configuration
├── models/               # Model integrations
│   ├── got_ocr.py       # GOT-OCR 2.0
│   ├── qwen_vl.py       # Qwen2-VL
│   └── model_loader.py  # Factory with cache
├── utils/                # Utilities
│   ├── model_cache.py   # Cache management
│   ├── logger.py        # Logging
│   └── validators.py    # Validation
├── ui/                   # UI components
├── tests/                # Test suite
├── notebooks/            # Jupyter notebooks
├── scripts/              # Utility scripts
└── docs/                 # Documentation
```

### Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=models --cov=utils --cov-report=html

# Specific test
pytest tests/test_models.py::test_model_loading
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type check
mypy models/ utils/
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t chatvlmllm -f docker/Dockerfile .

# Run with GPU
docker-compose -f docker/docker-compose.yml up
```

## 📈 Benchmarking

Run benchmark tests:

```python
from notebooks import run_benchmark

results = run_benchmark(
    models=['got_ocr', 'qwen_vl_2b'],
    test_set='examples/',
    metrics=['cer', 'wer', 'speed']
)
```

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🧪 Additional tests
- 🎨 UI enhancements
- 🌐 Translations

## 📝 Citation

If you use this project in your research, please cite:

```bibtex
@software{chatvlmllm2026,
  author = {Oleg Karenkikh},
  title = {ChatVLMLLM: Document OCR with Vision Language Models},
  year = {2026},
  url = {https://github.com/OlegKarenkikh/chatvlmllm}
}
```

## 🙏 Acknowledgments

### Models

- **GOT-OCR 2.0**: [stepfun-ai/GOT-OCR2_0](https://huggingface.co/stepfun-ai/GOT-OCR2_0)
- **Qwen2-VL**: [Qwen/Qwen2-VL](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct)

### Frameworks

- [Streamlit](https://streamlit.io/) - Web interface
- [HuggingFace](https://huggingface.co/) - Model hub
- [PyTorch](https://pytorch.org/) - ML framework

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [github.com/OlegKarenkikh/chatvlmllm](https://github.com/OlegKarenkikh/chatvlmllm)
- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/OlegKarenkikh/chatvlmllm/issues)
- **Discussions**: [GitHub Discussions](https://github.com/OlegKarenkikh/chatvlmllm/discussions)

## 📞 Support

Need help?

- 📖 Check [documentation](docs/)
- 🐛 [Report issues](https://github.com/OlegKarenkikh/chatvlmllm/issues)
- 💬 [Ask questions](https://github.com/OlegKarenkikh/chatvlmllm/discussions)

---

<p align="center">
  Made with ❤️ for education and research<br>
  <b>ChatVLMLLM</b> - Exploring Vision Language Models for Document OCR
</p>