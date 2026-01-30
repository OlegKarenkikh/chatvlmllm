#!/usr/bin/env python3
"""
Тест удаления Qwen2-VL 2B (Emergency Mode) из Transformers режима
Проверяет, что модель больше не доступна в конфигурации
"""

import yaml
import sys
import os

def test_qwen2_vl_removal():
    """Тестирует удаление Qwen2-VL 2B Emergency Mode"""
    
    print("🧪 Тестирование удаления Qwen2-VL 2B (Emergency Mode)...")
    
    # Проверяем config.yaml
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Проверяем, что qwen_vl_2b больше нет в конфигурации
        models = config.get('models', {})
        
        print("\n📋 Проверка config.yaml:")
        if 'qwen_vl_2b' not in models:
            print("  ✅ qwen_vl_2b удалена из конфигурации")
        else:
            print("  ❌ qwen_vl_2b все еще присутствует в конфигурации")
            return False
        
        # Проверяем, что нет упоминаний Qwen2-VL 2B Emergency Mode
        config_str = yaml.dump(config)
        if "Qwen2-VL 2B (Emergency Mode)" not in config_str:
            print("  ✅ Нет упоминаний 'Qwen2-VL 2B (Emergency Mode)'")
        else:
            print("  ❌ Найдены упоминания 'Qwen2-VL 2B (Emergency Mode)'")
            return False
        
        # Показываем оставшиеся модели
        print("\n📊 Оставшиеся модели в Transformers режиме:")
        for model_key, model_config in models.items():
            model_name = model_config.get('name', model_key)
            model_path = model_config.get('model_path', 'N/A')
            print(f"  • {model_name} ({model_key})")
            print(f"    Путь: {model_path}")
        
    except Exception as e:
        print(f"❌ Ошибка при чтении config.yaml: {e}")
        return False
    
    # Проверяем model_loader.py
    try:
        with open('models/model_loader.py', 'r', encoding='utf-8') as f:
            loader_content = f.read()
        
        print("\n📋 Проверка models/model_loader.py:")
        if '"qwen_vl_2b"' not in loader_content:
            print("  ✅ qwen_vl_2b удалена из MODEL_REGISTRY")
        else:
            print("  ❌ qwen_vl_2b все еще присутствует в MODEL_REGISTRY")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при чтении model_loader.py: {e}")
        return False
    
    # Проверяем model_loader_emergency.py
    try:
        with open('models/model_loader_emergency.py', 'r', encoding='utf-8') as f:
            emergency_content = f.read()
        
        print("\n📋 Проверка models/model_loader_emergency.py:")
        if '"qwen_vl_2b"' not in emergency_content:
            print("  ✅ qwen_vl_2b удалена из Emergency MODEL_REGISTRY")
        else:
            print("  ❌ qwen_vl_2b все еще присутствует в Emergency MODEL_REGISTRY")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при чтении model_loader_emergency.py: {e}")
        return False
    
    print("\n✅ Все проверки прошли успешно!")
    return True

def test_model_loading():
    """Тестирует загрузку моделей без qwen_vl_2b"""
    
    print("\n🔧 Тестирование загрузки моделей...")
    
    try:
        # Импортируем ModelLoader
        sys.path.append('models')
        from model_loader import ModelLoader
        
        # Получаем конфигурацию моделей
        config = ModelLoader.load_config()
        available_models = list(config.get('models', {}).keys())
        
        print(f"\n📊 Доступные модели в конфигурации ({len(available_models)}):")
        for model_id in available_models:
            model_config = config['models'][model_id]
            model_name = model_config.get('name', model_id)
            print(f"  • {model_name} ({model_id})")
        
        # Проверяем, что qwen_vl_2b не в списке
        if 'qwen_vl_2b' not in available_models:
            print("\n✅ qwen_vl_2b не найдена в списке доступных моделей")
        else:
            print("\n❌ qwen_vl_2b все еще доступна для загрузки")
            return False
        
        # Проверяем, что другие Qwen модели остались
        qwen_models = [m for m in available_models if 'qwen' in m.lower()]
        print(f"\n📋 Оставшиеся Qwen модели ({len(qwen_models)}):")
        for model in qwen_models:
            model_config = config['models'][model]
            model_name = model_config.get('name', model)
            print(f"  • {model_name} ({model})")
        
        if len(qwen_models) > 0:
            print("✅ Другие Qwen модели остались доступными")
        else:
            print("⚠️ Не найдено других Qwen моделей")
        
        # Проверяем MODEL_REGISTRY
        registry_models = list(ModelLoader.MODEL_REGISTRY.keys())
        print(f"\n📋 Модели в MODEL_REGISTRY ({len(registry_models)}):")
        for model in registry_models:
            print(f"  • {model}")
        
        if 'qwen_vl_2b' not in registry_models:
            print("✅ qwen_vl_2b не найдена в MODEL_REGISTRY")
        else:
            print("❌ qwen_vl_2b все еще в MODEL_REGISTRY")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании загрузки моделей: {e}")
        return False

def create_removal_report():
    """Создает отчет об удалении модели"""
    
    report_content = """# Удаление Qwen2-VL 2B (Emergency Mode) из Transformers режима

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
"""
    
    with open('QWEN2_VL_REMOVAL_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("📄 Отчет сохранен в QWEN2_VL_REMOVAL_REPORT.md")

if __name__ == "__main__":
    print("🗑️ Тестирование удаления Qwen2-VL 2B (Emergency Mode)")
    print("=" * 60)
    
    config_success = test_qwen2_vl_removal()
    
    if config_success:
        loading_success = test_model_loading()
        
        if loading_success:
            create_removal_report()
            print("\n🎉 Удаление успешно завершено!")
            print("\n📝 Что было сделано:")
            print("  • Удалена Qwen2-VL 2B (Emergency Mode) из config.yaml")
            print("  • Удалена из MODEL_REGISTRY в model_loader.py")
            print("  • Удалена из Emergency MODEL_REGISTRY")
            print("  • Модель больше не доступна для загрузки")
            print("\n💡 Рекомендации:")
            print("  • Используйте Qwen3-VL 2B для лучшего качества")
            print("  • GOT-OCR 2.0 для быстрого OCR")
            print("  • Phi-3.5 Vision для сложного анализа")
        else:
            print("\n❌ Ошибка при тестировании загрузки моделей")
            sys.exit(1)
    else:
        print("\n❌ Ошибка при удалении конфигурации")
        sys.exit(1)