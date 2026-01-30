# Руководство по кешу моделей

## Обзор

Модели HuggingFace автоматически кешируются после первой загрузки. Это руководство поможет управлять кешем моделей для экономии места и ускорения загрузки.

## Расположение кеша

### По умолчанию

```
~/.cache/huggingface/hub/
```

### Изменение расположения

```bash
# Через переменную окружения
export HF_HOME=/path/to/custom/cache
export TRANSFORMERS_CACHE=/path/to/custom/cache

# В Python
import os
os.environ['HF_HOME'] = '/path/to/custom/cache'
```

## Размеры моделей

| Модель | Размер на диске |
|--------|-----------------|
| GOT-OCR 2.0 | ~1.2 GB |
| Qwen2-VL 2B | ~4.5 GB |
| Qwen2-VL 7B | ~15 GB |
| Qwen3-VL 2B | ~4.5 GB |
| Qwen3-VL 4B | ~9 GB |
| Qwen3-VL 8B | ~18 GB |
| dots.ocr | ~8 GB |

**Полный кеш всех моделей:** ~60 GB

## Проверка кеша

### Скрипт проверки

```bash
python scripts/check_models.py
```

Вывод:
```
=== Проверка кеша моделей ===

Директория кеша: /home/user/.cache/huggingface/hub
Всего размер: 45.2 GB

Закешированные модели:
  ✅ stepfun-ai/GOT-OCR2_0 (1.2 GB)
  ✅ Qwen/Qwen2-VL-2B-Instruct (4.5 GB)
  ✅ Qwen/Qwen3-VL-2B-Instruct (4.5 GB)
  ❌ Qwen/Qwen3-VL-8B-Instruct (не загружена)

Рекомендации:
  - Загрузите Qwen3-VL-8B для лучшего качества
```

### Программная проверка

```python
from utils.model_cache import ModelCacheManager, check_model_availability

# Создание менеджера кеша
cache_manager = ModelCacheManager()

# Проверка конкретной модели
is_cached, message = check_model_availability("Qwen/Qwen3-VL-2B-Instruct")
print(f"Закеширована: {is_cached}")
print(f"Сообщение: {message}")

# Список всех закешированных моделей
cached_models = cache_manager.list_cached_models()
for model in cached_models:
    print(f"{model['model_id']}: {model['size_gb']} GB")

# Общая информация о кеше
info = cache_manager.get_cache_info()
print(f"Всего моделей: {info['model_count']}")
print(f"Общий размер: {info['total_size_gb']} GB")
```

## Предзагрузка моделей

### Скрипт загрузки

```bash
python scripts/download_models.py
```

### Выборочная загрузка

```python
from huggingface_hub import snapshot_download

# Загрузка конкретной модели
snapshot_download(
    repo_id="Qwen/Qwen3-VL-2B-Instruct",
    local_dir_use_symlinks=False
)
```

### Загрузка с фильтром файлов

```python
from huggingface_hub import snapshot_download

# Только safetensors (без pytorch_model.bin)
snapshot_download(
    repo_id="Qwen/Qwen3-VL-8B-Instruct",
    ignore_patterns=["*.bin", "*.pt"]
)
```

## Очистка кеша

### Полная очистка

```bash
# Удаление всего кеша HuggingFace
rm -rf ~/.cache/huggingface/hub/
```

### Выборочная очистка

```python
from utils.model_cache import ModelCacheManager

cache_manager = ModelCacheManager()

# Удаление конкретной модели
success = cache_manager.delete_model_cache("Qwen/Qwen2-VL-7B-Instruct")
print(f"Удалена: {success}")
```

### Очистка через CLI

```bash
# Установка huggingface-cli
pip install huggingface_hub

# Очистка неиспользуемых файлов
huggingface-cli cache clean
```

## Офлайн режим

### Настройка

```bash
# Запрет сетевых запросов
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
```

### Использование локальных моделей

```python
from transformers import AutoModel, AutoProcessor

# Загрузка из локальной директории
model = AutoModel.from_pretrained(
    "/path/to/local/model",
    local_files_only=True
)
```

## Советы по оптимизации

### Экономия места

1. **Используйте symlinks** (по умолчанию на Linux)
2. **Удаляйте неиспользуемые модели**
3. **Используйте квантизованные версии**

### Ускорение загрузки

1. **SSD накопитель** для кеша
2. **Предзагрузка моделей** перед использованием
3. **Локальная сеть** для HuggingFace Mirror

### Зеркала HuggingFace

```bash
# Использование зеркала (для Китая)
export HF_ENDPOINT=https://hf-mirror.com
```

## Структура кеша

```
~/.cache/huggingface/hub/
├── models--Qwen--Qwen3-VL-2B-Instruct/
│   ├── blobs/
│   │   ├── abc123...  # Файлы модели
│   │   └── def456...
│   ├── refs/
│   │   └── main      # Ссылка на текущую версию
│   └── snapshots/
│       └── abc123.../  # Версии модели
│           ├── config.json
│           ├── model.safetensors
│           └── tokenizer.json
└── models--stepfun-ai--GOT-OCR2_0/
    └── ...
```

## Использование с Docker

### Монтирование кеша

```yaml
# docker-compose.yml
services:
  app:
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
```

### Предзагрузка в образ

```dockerfile
FROM python:3.10

# Копирование локального кеша
COPY ./model_cache /root/.cache/huggingface/hub/

# Или загрузка при сборке
RUN python -c "from huggingface_hub import snapshot_download; \
    snapshot_download('Qwen/Qwen3-VL-2B-Instruct')"
```

## Устранение проблем

### Повреждённый кеш

```bash
# Удаление и повторная загрузка
rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen3-VL-2B-Instruct/
```

### Нехватка места

```bash
# Проверка использования диска
du -sh ~/.cache/huggingface/hub/

# Очистка старых версий
huggingface-cli cache clean --prune
```

### Медленная загрузка

1. Проверьте интернет-соединение
2. Используйте зеркало HuggingFace
3. Загружайте в нерабочее время
4. Используйте предзагруженный кеш

## API ModelCacheManager

```python
from utils.model_cache import ModelCacheManager

class ModelCacheManager:
    def __init__(self, cache_dir: str = None):
        """Инициализация с кастомной директорией кеша."""
        
    def find_model_in_cache(self, model_id: str) -> Path:
        """Поиск модели в кеше."""
        
    def is_model_cached(self, model_id: str) -> bool:
        """Проверка наличия модели в кеше."""
        
    def get_cached_snapshot_path(self, model_id: str) -> Path:
        """Получение пути к последнему снимку."""
        
    def get_model_size(self, model_id: str) -> int:
        """Размер модели в байтах."""
        
    def list_cached_models(self) -> list:
        """Список всех закешированных моделей."""
        
    def delete_model_cache(self, model_id: str) -> bool:
        """Удаление модели из кеша."""
        
    def get_cache_info(self) -> dict:
        """Общая информация о кеше."""
```
