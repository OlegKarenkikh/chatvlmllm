# Удаление Qwen2-VL 2B (Emergency Mode) из Transformers режима

## Проблема
Модель Qwen2-VL 2B (Emergency Mode) работала очень медленно и плохо распознавала текст в Transformers режиме, что негативно влияло на пользовательский опыт.

## Решение
Полное удаление модели из Transformers режима:

### 1. Удалено из config.yaml
- Удалена секция `qwen_vl_2b` с полной конфигурацией модели
- Убраны все параметры: model_path, precision, torch_dtype и др.

### 2. Удалено из model_loader.py
- Удалена запись `"qwen_vl_2b": QwenVLModel` из MODEL_REGISTRY
- Модель больше не может быть загружена через основной загрузчик

### 3. Удалено из model_loader_emergency.py
- Удалена запись из аварийного MODEL_REGISTRY
- Модель недоступна и в аварийном режиме

## Изменения в файлах

### config.yaml
```yaml
# УДАЛЕНО:
# qwen_vl_2b:
#   attn_implementation: eager
#   context_length: 4096
#   device_map: auto
#   load_in_4bit: false
#   load_in_8bit: false
#   max_new_tokens: 2048
#   model_path: Qwen/Qwen2-VL-2B-Instruct
#   name: Qwen2-VL 2B (Emergency Mode)
#   precision: fp16
#   torch_dtype: float16
#   trust_remote_code: true
#   use_flash_attention: false
```

### models/model_loader.py
```python
# УДАЛЕНО:
# "qwen_vl_2b": QwenVLModel,
```

### models/model_loader_emergency.py
```python
# УДАЛЕНО:
# "qwen_vl_2b": QwenVLModel,
```

## Оставшиеся Qwen модели
После удаления остаются доступными:
- **qwen_vl_7b**: Qwen2-VL 7B - более мощная версия
- **qwen3_vl_2b**: Qwen3-VL 2B (Emergency Mode) - новая версия

## Преимущества удаления
1. **Улучшенная производительность**: Убрана медленная модель
2. **Лучшее качество**: Убрана модель с плохим распознаванием
3. **Упрощенный выбор**: Меньше путаницы для пользователей
4. **Оптимизация ресурсов**: Освобождены ресурсы системы

## Альтернативы для пользователей
Вместо Qwen2-VL 2B (Emergency Mode) рекомендуется использовать:
- **Qwen3-VL 2B**: Улучшенная версия с лучшим качеством
- **GOT-OCR 2.0**: Для быстрого OCR
- **Phi-3.5 Vision**: Для сложного анализа

## Статус
✅ **УДАЛЕНО** - Qwen2-VL 2B (Emergency Mode) полностью удалена из Transformers режима

Дата удаления: 25 января 2026
