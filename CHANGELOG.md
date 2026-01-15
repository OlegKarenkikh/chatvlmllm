# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real model integration (GOT-OCR, Qwen2-VL)
- Batch processing API
- Fine-tuning support
- Cloud deployment guide
- Performance benchmarks

## [0.2.0] - 2026-01-15

### Added
- **Production Utilities**
  - Colored logging system with file output (`utils/logger.py`)
  - File-based caching for model results (`utils/cache.py`)
  - Export utilities for JSON/CSV/TXT formats (`utils/export.py`)
  - Input validation and sanitization (`utils/validators.py`)
  
- **Enhanced Application**
  - Complete UI rewrite with modern design
  - Session state management for chat history
  - OCR mode with preview and settings
  - Interactive chat mode with history
  - Model comparison page
  - In-app documentation
  
- **UI Components**
  - Reusable component library (`ui/components.py`)
  - Metric cards, progress bars, model cards
  - Feature lists and code examples
  - Comparison tables and alerts
  
- **Developer Tools**
  - Environment check script (`scripts/check_setup.py`)
  - Cleanup utility (`scripts/cleanup.py`)
  - Environment configuration template (`.env.example`)
  - Developer guide (`README_DEV.md`)
  
- **Project Structure**
  - Examples directory with instructions
  - Logs directory for application logs
  - Results directory for outputs
  - Enhanced `.gitignore` for caches and logs

### Changed
- Updated `app.py` with placeholder model integration
- Improved `utils/__init__.py` with all utility exports
- Enhanced documentation with usage examples
- Better error handling throughout the application

### Fixed
- Session state initialization issues
- File upload validation
- Export functionality placeholders

## [0.1.0] - 2026-01-15

### Added
- **Project Foundation**
  - Initial project structure
  - MIT License
  - README with project overview
  - CONTRIBUTING guidelines
  
- **Model Integration Framework**
  - Abstract base model class (`models/base_model.py`)
  - GOT-OCR 2.0 integration module (`models/got_ocr.py`)
  - Qwen2-VL integration module (`models/qwen_vl.py`)
  - Model factory pattern (`models/model_loader.py`)
  
- **Utility Modules**
  - Image preprocessing pipeline (`utils/image_processor.py`)
  - Text extraction and cleaning (`utils/text_extractor.py`)
  - Field parser for structured documents (`utils/field_parser.py`)
  - Markdown rendering utilities (`utils/markdown_renderer.py`)
  
- **UI Components**
  - Modern CSS styling system (`ui/styles.py`)
  - Streamlit application template (`app.py`)
  
- **Testing**
  - Test framework setup
  - Model integration tests (`tests/test_models.py`)
  - Utility function tests (`tests/test_utils.py`)
  - Test running script (`scripts/run_tests.sh`)
  
- **Documentation**
  - Quick start guide (`QUICKSTART.md`)
  - Model documentation (`docs/models.md`)
  - Architecture documentation (`docs/architecture.md`)
  - Research log template (`docs/research_log.md`)
  - Project summary (`PROJECT_SUMMARY.md`)
  
- **Interactive Notebooks**
  - Model exploration notebook (`notebooks/01_model_exploration.ipynb`)
  - Batch processing notebook (`notebooks/02_batch_processing.ipynb`)
  - Notebook usage guide (`notebooks/README.md`)
  
- **Docker Support**
  - Dockerfile for containerization (`docker/Dockerfile`)
  - Docker Compose configuration (`docker/docker-compose.yml`)
  - Docker ignore file (`.dockerignore`)
  
- **Setup Scripts**
  - Automated setup for Linux/Mac (`scripts/setup.sh`)
  - Automated setup for Windows (`scripts/setup.bat`)
  - Model download utility (`scripts/download_models.py`)
  
- **Configuration**
  - YAML configuration file (`config.yaml`)
  - Python dependencies (`requirements.txt`)
  - Git ignore file (`.gitignore`)

### Technical Details
- Python 3.10+ support
- Streamlit 1.30+ for web interface
- PyTorch 2.1+ for model inference
- HuggingFace Transformers integration
- Type hints throughout codebase
- Comprehensive error handling
- Modular architecture for extensibility

---

## Version History Summary

- **0.2.0** - Production improvements (logging, caching, validation, UI enhancements)
- **0.1.0** - Initial release (project foundation, model framework, documentation)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this project.

## Links

- [GitHub Repository](https://github.com/OlegKarenkikh/chatvlmllm)
- [Documentation](https://github.com/OlegKarenkikh/chatvlmllm/tree/main/docs)
- [Issue Tracker](https://github.com/OlegKarenkikh/chatvlmllm/issues)