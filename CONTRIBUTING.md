# Contributing to ChatVLMLLM

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, constructive, and collaborative. We welcome contributions from everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/OlegKarenkikh/chatvlmllm/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, GPU)
   - Error messages or logs

### Suggesting Enhancements

1. Open an issue with the `enhancement` label
2. Describe the feature and its benefits
3. Provide examples or mockups if applicable
4. Discuss implementation approach

### Pull Requests

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Write or update tests
5. Update documentation
6. Commit with clear messages: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- CUDA-capable GPU (recommended)

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/chatvlmllm.git
cd chatvlmllm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=models --cov=utils

# Run specific test file
pytest tests/test_models.py
```

### Code Style

We follow PEP 8 with some modifications:

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy models/ utils/
```

## Project Structure

```
chatvlmllm/
├── app.py              # Main Streamlit application
├── config.yaml         # Configuration
├── models/             # Model integration
│   ├── base_model.py
│   ├── got_ocr.py
│   ├── qwen_vl.py
│   └── model_loader.py
├── utils/              # Utilities
│   ├── image_processor.py
│   ├── text_extractor.py
│   ├── field_parser.py
│   └── markdown_renderer.py
├── ui/                 # UI components
├── tests/              # Test suite
└── docs/               # Documentation
```

## Coding Guidelines

### Python Style

- Use type hints for function parameters and returns
- Write docstrings for all public functions/classes
- Keep functions focused and small (< 50 lines ideally)
- Use meaningful variable names
- Comment complex logic

### Example

```python
def process_image(
    image: Image.Image,
    model_key: str,
    config: Dict[str, Any]
) -> str:
    """
    Process image through specified model.
    
    Args:
        image: Input PIL Image
        model_key: Model identifier
        config: Model configuration
        
    Returns:
        Extracted text or model response
        
    Raises:
        ValueError: If model_key is invalid
        RuntimeError: If inference fails
    """
    # Implementation
    pass
```

### Testing Guidelines

- Write tests for new features
- Maintain test coverage above 80%
- Use fixtures for common test data
- Mock external dependencies (API calls, model loading)
- Test edge cases and error handling

### Documentation

- Update README.md for user-facing changes
- Update docs/ for architectural changes
- Add docstrings to new functions/classes
- Include usage examples
- Document breaking changes

## Areas for Contribution

### High Priority

- 🐛 Bug fixes
- ✅ Test coverage improvement
- 📝 Documentation enhancement
- 🎨 UI/UX improvements

### Feature Ideas

- 🔧 Additional model integrations
- 📊 Enhanced metrics and analytics
- 🌐 Multilingual support improvements
- ⚡ Performance optimizations
- 🔌 API development
- 📱 Mobile-friendly UI

### Research Contributions

- 📈 Benchmark results on new datasets
- 🔬 Comparative analysis
- 📄 Research documentation
- 🎓 Tutorial creation

## Commit Message Format

Use conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```
feat(models): add DeepSeek-VL integration

fix(utils): resolve image preprocessing bug

docs(readme): update installation instructions
```

## Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: Maintainer reviews code quality
3. **Testing**: Manual testing if needed
4. **Merge**: Approved PRs are merged

## Questions?

- Open an issue for questions
- Check existing documentation
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉