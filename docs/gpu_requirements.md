# Требования к GPU

## Обзор

Это руководство поможет выбрать оптимальную модель для вашей видеокарты и настроить квантизацию для эффективного использования памяти.

## Таблица совместимости

### Потребление VRAM по моделям

| Модель | FP16 | BF16 | INT8 | INT4 |
|--------|------|------|------|------|
| GOT-OCR 2.0 | 3 GB | 3 GB | 2 GB | - |
| Qwen2-VL 2B | 4.7 GB | 4.7 GB | 3.6 GB | - |
| Qwen2-VL 7B | 16.1 GB | 16.1 GB | 10.1 GB | - |
| Qwen3-VL 2B | 4.4 GB | 4.4 GB | 2.2 GB | 1.5 GB |
| Qwen3-VL 4B | 8.9 GB | 8.9 GB | 3.8 GB | 3 GB |
| Qwen3-VL 8B | 17.6 GB | 17.6 GB | 10 GB | 6 GB |
| dots.ocr | 8 GB | 8 GB | 6 GB | - |

### Рекомендации по GPU

| VRAM | Рекомендуемые модели | Квантизация |
|------|---------------------|-------------|
| 4 GB | GOT-OCR, Qwen3-VL 2B@INT4 | INT4/INT8 |
| 6 GB | Qwen3-VL 2B, Qwen3-VL 4B@INT4 | INT8/INT4 |
| 8 GB | Qwen3-VL 4B@INT8, dots.ocr@INT8 | INT8 |
| 12 GB | Qwen3-VL 4B@FP16, Qwen3-VL 8B@INT8 | FP16/INT8 |
| 16 GB | Qwen3-VL 8B@INT8, Qwen2-VL 7B@INT8 | INT8/FP16 |
| 24 GB+ | Все модели@FP16 | FP16/BF16 |

## Популярные видеокарты

### NVIDIA GeForce RTX 50-серия (2025)

| GPU | VRAM | Лучшие модели | Примечания |
|-----|------|---------------|------------|
| RTX 5090 | 32 GB | Qwen3-VL 8B@FP16 | Все модели без ограничений |
| RTX 5080 | 16 GB | Qwen3-VL 8B@INT8 | Оптимальный выбор |
| RTX 5070 Ti | 16 GB | Qwen3-VL 8B@INT8 | Отличная производительность |
| RTX 5070 | 12 GB | Qwen3-VL 4B@FP16 | Хороший баланс |
| RTX 5060 Ti | 16/8 GB | Зависит от версии | 16GB версия предпочтительна |

### NVIDIA GeForce RTX 40-серия

| GPU | VRAM | Лучшие модели |
|-----|------|---------------|
| RTX 4090 | 24 GB | Все модели@FP16 |
| RTX 4080 Super | 16 GB | Qwen3-VL 8B@INT8 |
| RTX 4080 | 16 GB | Qwen3-VL 8B@INT8 |
| RTX 4070 Ti Super | 16 GB | Qwen3-VL 8B@INT8 |
| RTX 4070 Ti | 12 GB | Qwen3-VL 4B@FP16 |
| RTX 4070 | 12 GB | Qwen3-VL 4B@FP16 |
| RTX 4060 Ti | 16/8 GB | Qwen3-VL 4B@INT8/INT4 |
| RTX 4060 | 8 GB | Qwen3-VL 2B@FP16 |

### NVIDIA GeForce RTX 30-серия

| GPU | VRAM | Лучшие модели |
|-----|------|---------------|
| RTX 3090 | 24 GB | Qwen3-VL 8B@FP16 |
| RTX 3080 Ti | 12 GB | Qwen3-VL 4B@FP16 |
| RTX 3080 | 10/12 GB | Qwen3-VL 4B@INT8 |
| RTX 3070 Ti | 8 GB | Qwen3-VL 2B@FP16 |
| RTX 3070 | 8 GB | Qwen3-VL 2B@FP16 |
| RTX 3060 | 12 GB | Qwen3-VL 4B@INT8 |

## Настройка квантизации

### FP16 (по умолчанию)

Максимальное качество, требует больше памяти.

```yaml
# config.yaml
models:
  qwen3_vl_8b:
    precision: "fp16"
```

```python
model = ModelLoader.load_model('qwen3_vl_8b', precision='fp16')
```

### INT8 (рекомендуется)

Хороший баланс качества и памяти. Снижение VRAM на ~40%.

```yaml
models:
  qwen3_vl_8b:
    precision: "int8"
```

```python
model = ModelLoader.load_model('qwen3_vl_8b', precision='int8')
```

### INT4 (максимальная экономия)

Минимальное потребление памяти. Снижение VRAM на ~66%.

```yaml
models:
  qwen3_vl_8b:
    precision: "int4"
```

```python
model = ModelLoader.load_model('qwen3_vl_8b', precision='int4')
```

## Flash Attention 2

Flash Attention 2 ускоряет инференс и снижает потребление памяти на 20-40%.

### Требования

- NVIDIA GPU с Compute Capability >= 8.0 (Ampere и новее)
- PyTorch 2.0+
- flash-attn >= 2.3.0

### Установка

```bash
pip install flash-attn --no-build-isolation
```

### Включение

```yaml
# config.yaml
models:
  qwen3_vl_8b:
    use_flash_attention: true
```

```python
model = ModelLoader.load_model('qwen3_vl_8b', use_flash_attention=True)
```

## Проверка GPU

### Скрипт проверки

```bash
python scripts/check_gpu.py
```

Вывод:
```
=== Проверка GPU ===
CUDA доступна: Да
GPU: NVIDIA GeForce RTX 4090
VRAM: 24.0 GB
Compute Capability: 8.9
Flash Attention: Поддерживается

=== Рекомендуемые модели ===
- Qwen3-VL 8B @ FP16 (17.6 GB)
- Qwen3-VL 4B @ FP16 (8.9 GB)
- Qwen3-VL 2B @ FP16 (4.4 GB)
- GOT-OCR 2.0 @ FP16 (3 GB)
- dots.ocr @ BF16 (8 GB)
```

### Программная проверка

```python
import torch

# Проверка CUDA
print(f"CUDA доступна: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    # Информация о GPU
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # VRAM
    total_memory = torch.cuda.get_device_properties(0).total_memory
    print(f"VRAM: {total_memory / 1024**3:.1f} GB")
    
    # Compute Capability
    major, minor = torch.cuda.get_device_capability(0)
    print(f"Compute Capability: {major}.{minor}")
    
    # Flash Attention
    flash_attention_supported = major >= 8
    print(f"Flash Attention: {'Да' if flash_attention_supported else 'Нет'}")
```

## Оптимизация памяти

### Автоматическое распределение

```python
model = ModelLoader.load_model('qwen3_vl_8b', device_map='auto')
```

### Очистка кеша

```python
import torch

# Очистка CUDA кеша
torch.cuda.empty_cache()

# Выгрузка модели
ModelLoader.unload_model('qwen3_vl_8b')
```

### Мониторинг памяти

```python
import torch

# Текущее использование
allocated = torch.cuda.memory_allocated() / 1024**3
reserved = torch.cuda.memory_reserved() / 1024**3

print(f"Выделено: {allocated:.2f} GB")
print(f"Зарезервировано: {reserved:.2f} GB")
```

## Устранение проблем

### Out of Memory (OOM)

1. Используйте более агрессивную квантизацию (INT4)
2. Уменьшите размер изображений
3. Выгрузите неиспользуемые модели
4. Очистите CUDA кеш

### Медленный инференс

1. Включите Flash Attention 2
2. Используйте FP16 вместо FP32
3. Обновите драйверы NVIDIA
4. Проверьте термальный троттлинг

### Модель не загружается

1. Проверьте доступную VRAM
2. Используйте меньшую модель или квантизацию
3. Перезагрузите CUDA (`torch.cuda.empty_cache()`)
4. Перезапустите Python/Jupyter

## Сравнение производительности

### Время инференса (RTX 4090, изображение 1024x1024)

| Модель | FP16 | INT8 | INT4 |
|--------|------|------|------|
| Qwen3-VL 2B | 0.8s | 1.0s | 1.2s |
| Qwen3-VL 4B | 1.5s | 1.8s | 2.1s |
| Qwen3-VL 8B | 2.5s | 3.0s | 3.5s |
| GOT-OCR 2.0 | 0.5s | 0.6s | - |

### Качество OCR (CER, ниже лучше)

| Модель | FP16 | INT8 | INT4 |
|--------|------|------|------|
| Qwen3-VL 8B | 2.1% | 2.3% | 2.8% |
| Qwen3-VL 4B | 2.5% | 2.7% | 3.2% |
| Qwen3-VL 2B | 3.1% | 3.3% | 3.8% |
| GOT-OCR 2.0 | 2.8% | 3.0% | - |

*CER = Character Error Rate (частота ошибок на символ)*
