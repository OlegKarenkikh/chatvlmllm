# Тесты ChatVLMLLM

## Структура

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_config/            # Тесты config/
│   └── test_settings.py
├── test_core/              # Тесты core/
│   ├── test_error_handler.py
│   └── test_logger.py
├── test_services/          # Тесты services/
│   └── test_prompt_service.py
└── test_utils/             # Тесты utils/
    └── test_text_cleaner.py
```

## Запуск тестов

### Все тесты
```bash
pytest tests/ -v
```

### С покрытием
```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Конкретный модуль
```bash
pytest tests/test_core/ -v
```

### Исключить GPU тесты
```bash
pytest tests/ -v -m "not gpu"
```

### Только быстрые тесты
```bash
pytest tests/ -v -m "not slow"
```

## Маркеры

- `@pytest.mark.gpu` - тесты, требующие GPU
- `@pytest.mark.slow` - медленные тесты
- `@pytest.mark.integration` - интеграционные тесты

## Написание тестов

### Пример базового теста

```python
import pytest

def test_example():
    """Test description."""
    assert 1 + 1 == 2
```

### Использование fixtures

```python
def test_with_fixture(sample_image):
    """Test using fixture."""
    assert sample_image.size == (100, 100)
```

### Тест с mock

```python
from unittest.mock import patch

def test_with_mock():
    """Test with mocking."""
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        result = module.function()
        assert result == "mocked"
```

## Coverage цели

- **Минимум**: 50%
- **Цель**: 70%
- **Отлично**: 85%+

## CI/CD

Тесты автоматически запускаются в GitHub Actions при:
- Push в `main`, `final-test`, `develop`
- Создании Pull Request
