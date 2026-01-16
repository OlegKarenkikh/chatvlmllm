# Быстрый старт

## Требования

- Python 3.10+
- NVIDIA GPU с 4+ GB VRAM (рекомендуется 8+ GB)
- CUDA 11.8+ и cuDNN

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/OlegKarenkikh/chatvlmllm.git
cd chatvlmllm
```

### 2. Создание виртуального окружения

```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Проверка GPU

```bash
python scripts/check_gpu.py
```

Ожидаемый вывод:
```
=== Проверка GPU ===
CUDA доступна: Да
GPU: NVIDIA GeForce RTX 4090
VRAM: 24.0 GB
```

## Первый запуск

### Вариант 1: Streamlit приложение

```bash
streamlit run app.py
```

Откройте http://localhost:8501 в браузере.

### Вариант 2: REST API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Документация API: http://localhost:8000/docs

### Вариант 3: Python скрипт

```python
from models import ModelLoader
from PIL import Image

# Загрузка модели (первый раз скачает веса)
model = ModelLoader.load_model('qwen3_vl_2b')

# Обработка изображения
image = Image.open('document.jpg')
text = model.extract_text(image)
print(text)
```

## Примеры использования

### OCR документа

```python
from models import ModelLoader
from PIL import Image

model = ModelLoader.load_model('qwen3_vl_2b')
image = Image.open('invoice.jpg')

# Извлечение текста
text = model.extract_text(image, language='Russian')
print(text)
```

### Чат о изображении

```python
model = ModelLoader.load_model('qwen3_vl_2b')
image = Image.open('diagram.png')

response = model.chat(image, "Объясните эту диаграмму")
print(response)
```

### Извлечение полей

```python
from utils.field_parser import FieldParser

text = model.extract_text(image)
fields = FieldParser.parse_invoice(text)
print(fields)
```

### Использование API

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
```

## Docker

### Быстрый запуск

```bash
docker-compose up -d
```

Сервисы:
- Streamlit: http://localhost:8501
- API: http://localhost:8000

### Сборка вручную

```bash
docker build -t chatvlmllm .
docker run --gpus all -p 8501:8501 chatvlmllm
```

## Выбор модели

| Ваш GPU | Рекомендуемая модель | Команда |
|---------|---------------------|---------|
| 4 GB VRAM | Qwen3-VL 2B + INT4 | `ModelLoader.load_model('qwen3_vl_2b', precision='int4')` |
| 8 GB VRAM | Qwen3-VL 2B | `ModelLoader.load_model('qwen3_vl_2b')` |
| 12 GB VRAM | Qwen3-VL 4B | `ModelLoader.load_model('qwen3_vl_4b')` |
| 16+ GB VRAM | Qwen3-VL 8B | `ModelLoader.load_model('qwen3_vl_8b')` |

## Устранение проблем

### CUDA не найдена

```bash
# Проверка CUDA
nvidia-smi

# Если не работает, установите драйверы NVIDIA
```

### Out of Memory

```python
# Используйте меньшую модель или квантизацию
model = ModelLoader.load_model('qwen3_vl_2b', precision='int4')
```

### Медленная первая загрузка

Первый запуск скачивает веса модели (несколько GB). Последующие запуски используют кеш.

### Модель не загружается

```bash
# Очистите кеш и попробуйте снова
rm -rf ~/.cache/huggingface/hub/models--Qwen*
```

## Следующие шаги

1. Изучите [Руководство по API](docs/api_guide.md)
2. Ознакомьтесь с [Требованиями к GPU](docs/gpu_requirements.md)
3. Попробуйте разные модели из [Документации по моделям](docs/models.md)
4. Настройте конфигурацию в `config.yaml`

## Полезные команды

```bash
# Запуск тестов
pytest tests/

# Проверка моделей в кеше
python scripts/check_models.py

# Предзагрузка моделей
python scripts/download_models.py
```

## Получение помощи

- Документация: `docs/`
- Issues: https://github.com/OlegKarenkikh/chatvlmllm/issues
- Примеры: `examples/`
