# ChatVLMLLM - OCR документов и Vision-Language модели

Комплексный инструментарий для OCR документов, визуального понимания и мультимодальных AI-приложений с использованием современных vision-language моделей.

## Возможности

### Поддерживаемые модели

- **GOT-OCR 2.0** - Специализированный OCR для сложных макетов
- **Qwen2-VL** (2B, 7B) - Продвинутое vision-language понимание
- **Qwen3-VL** (2B, 4B, 8B) - Новейшая VLM с OCR на 32 языках, визуальным агентом, контекстом 256K
- **dots.ocr** - SOTA мультиязычный парсер документов (100+ языков)

### Ключевые возможности

- **Мультиязычный OCR** - 32+ языка с высокой точностью
- **Визуальный агент** - Взаимодействие с GUI и автоматизация (Qwen3-VL)
- **Анализ документов** - Определение макета, извлечение таблиц, парсинг структуры
- **Визуальное рассуждение** - Сложные рассуждения об изображениях и диаграммах
- **Понимание видео** - Контекст 256K для длинных видео (Qwen3-VL)
- **Гибкая квантизация** - Поддержка FP16, INT8, INT4
- **Flash Attention 2** - Быстрый инференс с меньшим потреблением памяти
- **REST API** - Production-ready FastAPI эндпоинты
- **Docker** - Контейнеризация с поддержкой GPU

## Быстрый старт

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/OlegKarenkikh/chatvlmllm.git
cd chatvlmllm

# Установка зависимостей
pip install -r requirements.txt

# Установка последней версии transformers для Qwen3-VL
pip install git+https://github.com/huggingface/transformers
```

### Проверка совместимости GPU

```bash
python scripts/check_gpu.py
```

### Базовое использование

#### Python API

```python
from models import ModelLoader
from PIL import Image

# Загрузка Qwen3-VL 2B
model = ModelLoader.load_model('qwen3_vl_2b')

# Обработка изображения
image = Image.open('document.jpg')
result = model.extract_text(image)

print(result)
```

#### Streamlit приложение

```bash
streamlit run app.py
```

Доступ: http://localhost:8501

#### REST API

```bash
# Запуск API сервера
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Использование API
curl -X POST "http://localhost:8000/ocr?model=qwen3_vl_2b" \
  -F "file=@document.jpg"
```

Документация API: http://localhost:8000/docs

#### Docker

```bash
# Сборка и запуск
docker-compose up -d

# Доступ к сервисам
# Streamlit: http://localhost:8501
# API: http://localhost:8000/docs
```

## Требования к GPU

| GPU | VRAM | Лучшая модель | Статус |
|-----|------|---------------|--------|
| RTX 5090 | 32GB | Qwen3-VL 8B@FP16 | Идеально |
| RTX 5080 | 16GB | Qwen3-VL 8B@INT8 | Отлично |
| RTX 5070 | 12GB | Qwen3-VL 4B@FP16 | Хорошо |
| RTX 5060 Ti | 16GB | Qwen3-VL 8B@INT8 | Лучшее соотношение |
| RTX 5060 Ti | 8GB | Qwen3-VL 4B@INT4 | Ограниченно |

Подробнее см. [Руководство по требованиям GPU](docs/gpu_requirements.md)

## Документация

- [Требования к GPU](docs/gpu_requirements.md) - Полное руководство по совместимости
- [Руководство по Qwen3-VL](docs/qwen3_vl_guide.md) - Использование и оптимизация
- [Руководство по API](docs/api_guide.md) - Документация REST API
- [Руководство по кешу моделей](docs/model_cache_guide.md) - Управление загрузками моделей

## Использование API

### Python клиент

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

# Чат
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/chat',
        files={'file': f},
        data={'prompt': 'Что на этом изображении?'}
    )
    print(response.json()['response'])
```

Больше примеров см. [examples/api_usage.py](examples/api_usage.py).

### cURL

```bash
# Проверка здоровья
curl http://localhost:8000/health

# OCR
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@document.jpg" \
  -F "model=qwen3_vl_2b"

# Чат
curl -X POST "http://localhost:8000/chat" \
  -F "file=@image.jpg" \
  -F "prompt=Опишите это изображение"
```

Больше примеров см. [examples/api_curl.sh](examples/api_curl.sh).

## Docker развёртывание

### Использование docker-compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка сервисов
docker-compose down
```

### Сервисы

- **API**: http://localhost:8000
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc
- **Streamlit**: http://localhost:8501

### Требования

- Docker 20.10+
- NVIDIA Docker runtime
- Рекомендуется 16GB+ VRAM

## Конфигурация

### config.yaml

```yaml
models:
  qwen3_vl_8b:
    model_path: "Qwen/Qwen3-VL-8B-Instruct"
    precision: "int8"  # fp16, bf16, int8, int4
    use_flash_attention: true
    device_map: "auto"
```

### INT4 квантизация (снижение VRAM на 66%)

```yaml
models:
  qwen3_vl_8b:
    precision: "int4"  # 17.6GB -> 6GB
```

## Что нового

### v1.0.0 (2026-01-15)

#### Основные возможности

- **Поддержка Qwen3-VL** - Все три модели (2B, 4B, 8B)
- **REST API** - Production-ready FastAPI
- **Docker** - Полная контейнеризация с поддержкой GPU
- **Streamlit приложение** - Обновлено со всеми моделями
- **Документация** - Полные руководства по API и использованию

#### Особенности Qwen3-VL

- **OCR на 32 языках** (vs 19 в Qwen2-VL)
- **Визуальный агент**
- **Контекст 256K** (расширяемый до 1M)
- **3D grounding** для пространственных рассуждений
- **Режим размышления** для сложных задач
- **Поддержка INT4** - на 66% меньше VRAM

## Примеры использования

### OCR документов

```python
# Извлечение текста из документа
text = model.extract_text(image, language="Russian")
```

### Анализ документов

```python
# Анализ структуры документа
analysis = model.analyze_document(image, focus="layout")
```

### Визуальное рассуждение

```python
# Сложные рассуждения
reasoning = model.visual_reasoning(
    image, 
    question="Объясните рабочий процесс на этой диаграмме"
)
```

### Визуальный агент (Qwen3-VL)

```python
# Взаимодействие с GUI
actions = model.chat(
    image=screenshot,
    prompt="Найдите и нажмите кнопку Отправить"
)
```

## Советы и лучшие практики

### Для 8GB VRAM

```python
# Используйте INT4 квантизацию
model = ModelLoader.load_model(
    'qwen3_vl_8b',
    precision='int4'  # 6GB вместо 17.6GB
)
```

### Для 12GB VRAM

```python
# Запуск нескольких моделей
qwen4b = ModelLoader.load_model('qwen3_vl_4b')  # 8.9GB
qwen2b = ModelLoader.load_model('qwen3_vl_2b')  # 4.4GB
# Итого: ~11GB с INT8
```

### Для 16GB+ VRAM

```python
# Оптимальное качество
model = ModelLoader.load_model(
    'qwen3_vl_8b',
    precision='int8',  # 10GB
    use_flash_attention=True
)
```

## Разработка

### Структура проекта

```
chatvlmllm/
├── api.py                  # FastAPI REST API
├── app.py                  # Streamlit приложение
├── models/
│   ├── got_ocr.py          # Интеграция GOT-OCR
│   ├── qwen_vl.py          # Интеграция Qwen2-VL
│   ├── qwen3_vl.py         # Интеграция Qwen3-VL
│   ├── dots_ocr.py         # Интеграция dots.ocr
│   └── model_loader.py     # Фабрика моделей
├── utils/
│   ├── logger.py
│   └── model_cache.py
├── scripts/
│   ├── check_gpu.py        # Проверка совместимости GPU
│   └── check_models.py     # Проверка кеша моделей
├── docs/
│   ├── gpu_requirements.md
│   ├── qwen3_vl_guide.md
│   └── api_guide.md
├── examples/
│   ├── api_usage.py
│   └── api_curl.sh
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Docker сервисы
└── config.yaml             # Конфигурация
```

### Тестирование

```bash
pytest tests/
```

## Участие в разработке

Приветствуем вклад в проект! Пожалуйста, откройте issue или PR.

См. [CONTRIBUTING.md](CONTRIBUTING.md) для руководства.

## Лицензия

MIT License

## Ссылки

- **GitHub**: https://github.com/OlegKarenkikh/chatvlmllm
- **Qwen3-VL**: https://github.com/QwenLM/Qwen3-VL
- **GOT-OCR**: https://github.com/Ucas-HaoranWei/GOT-OCR2.0
- **dots.ocr**: https://github.com/rednote-hilab/dots.ocr

## Благодарности

- Команда Qwen за Qwen3-VL
- Stepfun AI за GOT-OCR 2.0
- RedNote за dots.ocr

---

**Поставьте звезду репозиторию, если он вам полезен!**

## Статус

![GitHub stars](https://img.shields.io/github/stars/OlegKarenkikh/chatvlmllm?style=social)
![GitHub forks](https://img.shields.io/github/forks/OlegKarenkikh/chatvlmllm?style=social)
![License](https://img.shields.io/github/license/OlegKarenkikh/chatvlmllm)

**Production Ready** | **7 моделей** | **REST API** | **Docker**
