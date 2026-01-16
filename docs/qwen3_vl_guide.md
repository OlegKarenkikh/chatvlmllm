# Руководство по Qwen3-VL

## Обзор

Qwen3-VL — это новейшая серия vision-language моделей от команды Qwen (Alibaba). Модели обеспечивают SOTA производительность в задачах визуального понимания, OCR и визуального агента.

## Ключевые улучшения (vs Qwen2-VL)

| Возможность | Qwen2-VL | Qwen3-VL |
|-------------|----------|----------|
| OCR языки | 19 | 32 |
| Контекст | 32K | 256K (до 1M) |
| Визуальный агент | Нет | Да |
| 3D восприятие | Базовое | Продвинутое |
| Режим размышления | Нет | Да |
| INT4 квантизация | Нет | Да |

## Доступные модели

| Модель | Параметры | VRAM (FP16) | Применение |
|--------|-----------|-------------|------------|
| Qwen3-VL 2B | 2B | 4.4 GB | Быстрые задачи, мобильные устройства |
| Qwen3-VL 4B | 4B | 8.9 GB | Баланс скорости и качества |
| Qwen3-VL 8B | 8B | 17.6 GB | Максимальное качество |

## Установка

### Зависимости

```bash
# Базовые зависимости
pip install torch>=2.0.0 transformers>=4.45.0

# Последняя версия transformers (рекомендуется)
pip install git+https://github.com/huggingface/transformers

# Flash Attention 2 (опционально)
pip install flash-attn --no-build-isolation

# Утилиты Qwen VL
pip install qwen-vl-utils
```

### Проверка установки

```python
from transformers import Qwen3VLForConditionalGeneration, AutoProcessor

print("Установка успешна!")
```

## Базовое использование

### Загрузка модели

```python
from models import ModelLoader

# Загрузка с настройками по умолчанию
model = ModelLoader.load_model('qwen3_vl_2b')

# Загрузка с параметрами
model = ModelLoader.load_model(
    'qwen3_vl_8b',
    precision='int8',
    use_flash_attention=True
)
```

### OCR текста

```python
from PIL import Image

image = Image.open('document.jpg')

# Простое извлечение текста
text = model.extract_text(image)
print(text)

# С указанием языка
text = model.extract_text(image, language='Russian')
print(text)
```

### Анализ документа

```python
# Общий анализ
analysis = model.analyze_document(image, focus='general')

# Анализ макета
layout = model.analyze_document(image, focus='layout')

# Извлечение таблиц
tables = model.analyze_document(image, focus='tables')

# Анализ содержимого
content = model.analyze_document(image, focus='content')
```

### Чат о изображении

```python
# Простой вопрос
response = model.chat(image, "Что изображено на картинке?")

# С параметрами генерации
response = model.chat(
    image,
    "Опишите содержимое этого документа подробно",
    temperature=0.7,
    max_new_tokens=1024
)
```

### Визуальное рассуждение

```python
# Сложный вопрос с рассуждением
reasoning = model.visual_reasoning(
    image,
    question="Какие выводы можно сделать из данных на этом графике?"
)
```

## Продвинутые возможности

### OCR на 32 языках

Qwen3-VL поддерживает распознавание текста на 32 языках:

**Европейские:** английский, русский, немецкий, французский, испанский, итальянский, португальский, польский, нидерландский, чешский, румынский, венгерский

**Азиатские:** китайский (упр./трад.), японский, корейский, вьетнамский, тайский, индонезийский

**Другие:** арабский, иврит, хинди, турецкий, греческий и др.

```python
# Мультиязычный OCR
text = model.extract_text(image)  # Автоопределение языка

# С указанием языка для лучшего результата
text = model.extract_text(image, language='Japanese')
```

### Визуальный агент

Qwen3-VL может взаимодействовать с графическими интерфейсами:

```python
# Анализ скриншота
screenshot = Image.open('desktop.png')

# Поиск элемента
response = model.chat(
    screenshot,
    "Найдите кнопку 'Отправить' и опишите её расположение"
)

# Инструкция по действию
response = model.chat(
    screenshot,
    "Как закрыть это диалоговое окно?"
)
```

### Контекст 256K токенов

Qwen3-VL поддерживает длинный контекст для:
- Многостраничных документов
- Длинных видео
- Сложных диалогов

```python
# Обработка большого документа
pages = [Image.open(f'page_{i}.jpg') for i in range(10)]

# Последовательная обработка с сохранением контекста
full_text = ""
for page in pages:
    text = model.extract_text(page)
    full_text += text + "\n\n"
```

### Режим размышления (Thinking Mode)

Для сложных задач можно активировать режим размышления:

```python
# Сложная задача с рассуждением
response = model.chat(
    image,
    "Решите математическую задачу на этом изображении. "
    "Объясните каждый шаг решения.",
    max_new_tokens=2048
)
```

## Оптимизация

### Квантизация INT4

Снижение VRAM на 66% с минимальной потерей качества:

```python
model = ModelLoader.load_model('qwen3_vl_8b', precision='int4')
# 17.6 GB -> 6 GB
```

### Flash Attention 2

Ускорение инференса на 30-50%:

```python
model = ModelLoader.load_model(
    'qwen3_vl_8b',
    use_flash_attention=True
)
```

### Оптимальные настройки по VRAM

```python
# 8 GB VRAM
model = ModelLoader.load_model('qwen3_vl_4b', precision='int4')

# 12 GB VRAM
model = ModelLoader.load_model('qwen3_vl_4b', precision='fp16')

# 16 GB VRAM
model = ModelLoader.load_model('qwen3_vl_8b', precision='int8')

# 24 GB VRAM
model = ModelLoader.load_model('qwen3_vl_8b', precision='fp16')
```

## Сравнение с другими моделями

### OCR точность (CER, ниже лучше)

| Модель | Английский | Русский | Китайский |
|--------|------------|---------|-----------|
| Qwen3-VL 8B | 1.8% | 2.1% | 1.5% |
| Qwen3-VL 4B | 2.2% | 2.5% | 1.9% |
| Qwen3-VL 2B | 2.8% | 3.1% | 2.4% |
| GOT-OCR 2.0 | 2.5% | 3.0% | 2.2% |
| Qwen2-VL 7B | 2.0% | 2.4% | 1.7% |

### Скорость (токенов/сек, RTX 4090)

| Модель | FP16 | INT8 | INT4 |
|--------|------|------|------|
| Qwen3-VL 2B | 45 | 38 | 32 |
| Qwen3-VL 4B | 32 | 26 | 22 |
| Qwen3-VL 8B | 22 | 18 | 15 |

## Типичные сценарии

### Обработка паспорта

```python
from utils.field_parser import FieldParser

image = Image.open('passport.jpg')

# Извлечение текста
text = model.extract_text(image, language='Russian')

# Парсинг полей
fields = FieldParser.parse_passport(text)
print(fields)
# {'surname': 'ИВАНОВ', 'given_names': 'ИВАН ИВАНОВИЧ', ...}
```

### Обработка счёта

```python
image = Image.open('invoice.jpg')

# Структурированный анализ
response = model.chat(
    image,
    """Извлеките из счёта следующую информацию в формате JSON:
    - Номер счёта
    - Дата
    - Поставщик
    - Покупатель
    - Сумма
    - НДС
    - Итого"""
)
```

### Анализ диаграммы

```python
image = Image.open('chart.png')

analysis = model.visual_reasoning(
    image,
    "Проанализируйте тренды на этом графике и сделайте выводы"
)
```

## Устранение проблем

### Модель не загружается

```python
# Проверьте доступную память
import torch
print(f"Доступно VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# Используйте меньшую модель или квантизацию
model = ModelLoader.load_model('qwen3_vl_2b', precision='int4')
```

### Низкое качество OCR

1. Увеличьте разрешение изображения
2. Используйте предобработку:

```python
from utils.image_processor import ImageProcessor

image = Image.open('document.jpg')
processed = ImageProcessor.preprocess(image, enhance=True, denoise=True)
text = model.extract_text(processed)
```

### Медленный инференс

1. Включите Flash Attention
2. Уменьшите `max_new_tokens`
3. Используйте INT8/INT4 квантизацию

## Ссылки

- [Официальный репозиторий Qwen3-VL](https://github.com/QwenLM/Qwen3-VL)
- [Модели на HuggingFace](https://huggingface.co/Qwen)
- [Техническая документация](https://qwen.readthedocs.io/)
