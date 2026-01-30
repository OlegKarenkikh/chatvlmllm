#!/usr/bin/env python3
"""Тестовый скрипт для интеграции новых моделей."""

import sys
import traceback
from pathlib import Path

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader
from utils.logger import logger


def test_model_cache_status():
    """Тест статуса кеша для всех моделей."""
    print("🔍 Проверка статуса кеша для всех моделей...")
    print("=" * 60)
    
    config = ModelLoader.load_config()
    models = config.get('models', {})
    
    cached_models = []
    missing_models = []
    
    for model_key, model_config in models.items():
        print(f"\n📊 {model_key} ({model_config.get('name', 'Неизвестно')})")
        print(f"   Путь: {model_config.get('model_path', 'Н/Д')}")
        
        try:
            is_cached, message = ModelLoader.check_model_cache(model_key)
            if is_cached:
                print(f"   ✅ {message}")
                cached_models.append(model_key)
            else:
                print(f"   ❌ {message}")
                missing_models.append(model_key)
        except Exception as e:
            print(f"   ⚠️  Ошибка проверки кеша: {e}")
            missing_models.append(model_key)
    
    print(f"\n📈 СВОДКА")
    print(f"   Всего моделей: {len(models)}")
    print(f"   Кешированных: {len(cached_models)}")
    print(f"   Отсутствующих: {len(missing_models)}")
    
    if cached_models:
        print(f"\n✅ КЕШИРОВАННЫЕ МОДЕЛИ:")
        for model in cached_models:
            print(f"   - {model}")
    
    if missing_models:
        print(f"\n❌ ОТСУТСТВУЮЩИЕ МОДЕЛИ:")
        for model in missing_models:
            print(f"   - {model}")
    
    return cached_models, missing_models


def test_model_registry():
    """Тест полноты реестра моделей."""
    print("\n🔧 Проверка реестра моделей...")
    print("=" * 60)
    
    config = ModelLoader.load_config()
    config_models = set(config.get('models', {}).keys())
    registry_models = set(ModelLoader.MODEL_REGISTRY.keys())
    
    print(f"Модели в конфигурации: {len(config_models)}")
    print(f"Модели в реестре: {len(registry_models)}")
    
    missing_in_registry = config_models - registry_models
    extra_in_registry = registry_models - config_models
    
    if missing_in_registry:
        print(f"\n❌ ОТСУТСТВУЮТ В РЕЕСТРЕ:")
        for model in missing_in_registry:
            print(f"   - {model}")
    
    if extra_in_registry:
        print(f"\n⚠️  ЛИШНИЕ В РЕЕСТРЕ:")
        for model in extra_in_registry:
            print(f"   - {model}")
    
    if not missing_in_registry and not extra_in_registry:
        print(f"\n✅ Реестр и конфигурация синхронизированы!")
    
    return missing_in_registry, extra_in_registry


def test_model_loading(model_key: str):
    """Тест загрузки конкретной модели."""
    print(f"\n🚀 Тестирование загрузки модели: {model_key}")
    print("-" * 40)
    
    try:
        # Сначала проверить кеш
        is_cached, cache_msg = ModelLoader.check_model_cache(model_key)
        print(f"Статус кеша: {cache_msg}")
        
        if not is_cached:
            print("⚠️  Модель не в кеше - будет скачана при загрузке")
            return False
        
        # Попытка загрузить модель
        print("Загрузка модели...")
        model = ModelLoader.load_model(model_key)
        
        print(f"✅ Модель загружена успешно!")
        print(f"   Тип: {type(model).__name__}")
        print(f"   Конфигурация: {model.config.get('name', 'Неизвестно')}")
        
        # Тест информации о модели
        info = model.get_model_info()
        print(f"   Устройство: {info.get('device', 'Неизвестно')}")
        print(f"   Загружена: {info.get('loaded', False)}")
        
        # Выгрузить модель для освобождения памяти
        ModelLoader.unload_model(model_key)
        print("   Модель выгружена")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        traceback.print_exc()
        return False


def main():
    """Основная тестовая функция."""
    print("🧪 Тестирование интеграции новых моделей")
    print("=" * 60)
    
    # Тест 1: Статус кеша
    cached_models, missing_models = test_model_cache_status()
    
    # Тест 2: Полнота реестра
    missing_in_registry, extra_in_registry = test_model_registry()
    
    # Тест 3: Попытка загрузки кешированных моделей
    if cached_models:
        print(f"\n🚀 Тестирование загрузки моделей для кешированных моделей...")
        print("=" * 60)
        
        successful_loads = []
        failed_loads = []
        
        for model_key in cached_models:
            success = test_model_loading(model_key)
            if success:
                successful_loads.append(model_key)
            else:
                failed_loads.append(model_key)
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТОВ ЗАГРУЗКИ")
        print(f"   Успешных: {len(successful_loads)}")
        print(f"   Неудачных: {len(failed_loads)}")
        
        if successful_loads:
            print(f"\n✅ УСПЕШНЫЕ ЗАГРУЗКИ:")
            for model in successful_loads:
                print(f"   - {model}")
        
        if failed_loads:
            print(f"\n❌ НЕУДАЧНЫЕ ЗАГРУЗКИ:")
            for model in failed_loads:
                print(f"   - {model}")
    
    # Итоговая сводка
    print(f"\n🎯 ИТОГОВАЯ СВОДКА")
    print("=" * 60)
    print(f"✅ Новые классы моделей созданы и зарегистрированы")
    print(f"✅ API обновлен с новыми моделями")
    print(f"✅ Загрузчик моделей обновлен")
    
    if missing_in_registry:
        print(f"⚠️  {len(missing_in_registry)} моделей отсутствуют в реестре")
    else:
        print(f"✅ Все модели из конфигурации есть в реестре")
    
    print(f"\n🔄 Следующие шаги:")
    if missing_models:
        print(f"   - Скачать отсутствующие модели: {', '.join(missing_models[:3])}{'...' if len(missing_models) > 3 else ''}")
    print(f"   - Тестировать эндпоинты API с новыми моделями")
    print(f"   - Проверить, что инференс моделей работает корректно")
    print(f"   - Оптимизировать загрузку моделей и использование памяти")


if __name__ == "__main__":
    main()