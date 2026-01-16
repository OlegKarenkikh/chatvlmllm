# Руководство по участию в проекте

Спасибо за интерес к участию в проекте ChatVLMLLM!

## Способы участия

### Сообщения об ошибках

1. Проверьте, не создан ли уже [issue](https://github.com/OlegKarenkikh/chatvlmllm/issues)
2. Создайте новый issue с подробным описанием:
   - Версия Python и ОС
   - GPU и версия драйверов
   - Шаги для воспроизведения
   - Ожидаемое и фактическое поведение
   - Логи ошибок

### Предложения улучшений

1. Создайте issue с тегом `enhancement`
2. Опишите:
   - Проблему, которую решает улучшение
   - Предлагаемое решение
   - Альтернативы, которые рассматривали

### Pull Requests

1. Форкните репозиторий
2. Создайте ветку для вашей функции:
   ```bash
   git checkout -b feature/my-feature
   ```
3. Внесите изменения
4. Запустите тесты:
   ```bash
   pytest tests/
   ```
5. Закоммитьте с понятным сообщением:
   ```bash
   git commit -m "Добавлена новая функция X"
   ```
6. Отправьте изменения:
   ```bash
   git push origin feature/my-feature
   ```
7. Создайте Pull Request

## Стандарты кода

### Стиль кода

- Следуйте PEP 8
- Используйте type hints
- Документируйте функции с docstrings
- Максимальная длина строки: 100 символов

### Пример оформления

```python
def process_document(
    image: Image.Image,
    model_name: str = "qwen3_vl_2b",
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Обработка документа с извлечением текста.
    
    Args:
        image: PIL изображение документа
        model_name: Имя модели для использования
        language: Язык документа (опционально)
        
    Returns:
        Словарь с извлечённым текстом и метаданными
        
    Raises:
        ValueError: Если модель не найдена
        RuntimeError: Если произошла ошибка обработки
    """
    # Реализация
    pass
```

### Форматирование

```bash
# Установка инструментов
pip install black flake8 isort

# Форматирование кода
black .
isort .

# Проверка линтером
flake8 .
```

## Тестирование

### Запуск тестов

```bash
# Все тесты
pytest tests/

# С покрытием
pytest tests/ --cov=. --cov-report=html

# Конкретный файл
pytest tests/test_models.py -v
```

### Написание тестов

```python
import pytest
from PIL import Image
import numpy as np

@pytest.fixture
def sample_image():
    """Создание тестового изображения."""
    img_array = np.ones((100, 200, 3), dtype=np.uint8) * 255
    return Image.fromarray(img_array)

def test_model_loading():
    """Тест загрузки модели."""
    from models import ModelLoader
    
    config = ModelLoader.load_config()
    assert "models" in config
    assert "qwen3_vl_2b" in config["models"]

def test_image_preprocessing(sample_image):
    """Тест предобработки изображения."""
    from utils.image_processor import ImageProcessor
    
    processed = ImageProcessor.preprocess(sample_image)
    assert processed.mode == 'RGB'
```

## Структура проекта

```
chatvlmllm/
├── api.py              # REST API
├── app.py              # Streamlit приложение
├── config.yaml         # Конфигурация
├── models/             # Интеграция моделей
│   ├── __init__.py
│   ├── base_model.py   # Базовый класс
│   ├── got_ocr.py      # GOT-OCR
│   ├── qwen_vl.py      # Qwen2-VL
│   ├── qwen3_vl.py     # Qwen3-VL
│   ├── dots_ocr.py     # dots.ocr
│   └── model_loader.py # Загрузчик моделей
├── utils/              # Утилиты
│   ├── __init__.py
│   ├── image_processor.py
│   ├── text_extractor.py
│   ├── field_parser.py
│   └── ...
├── tests/              # Тесты
│   ├── __init__.py
│   ├── test_models.py
│   └── test_utils.py
├── docs/               # Документация
└── examples/           # Примеры использования
```

## Области для вклада

### Приоритетные

- Новые интеграции моделей
- Улучшение точности OCR
- Оптимизация производительности
- Документация на русском языке

### Желательные

- Новые типы документов для парсинга
- Интеграционные тесты
- CI/CD настройка
- Примеры использования

### Идеи

- Поддержка PDF
- Пакетная обработка
- Fine-tuning на своих данных
- Веб-интерфейс для аннотации

## Процесс ревью

1. Автоматическая проверка тестов
2. Ревью кода мейнтейнером
3. Обсуждение и доработки при необходимости
4. Мерж после одобрения

## Лицензия

Участвуя в проекте, вы соглашаетесь с тем, что ваш код будет распространяться под лицензией MIT.

## Контакты

- GitHub Issues: https://github.com/OlegKarenkikh/chatvlmllm/issues
- Email: через GitHub профиль

## Благодарности

Спасибо всем участникам проекта!
