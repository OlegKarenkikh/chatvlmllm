#!/usr/bin/env python3
"""Тест легких моделей для RTX 5070 Ti."""

import sys
from pathlib import Path
from PIL import Image
import time

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def test_light_model(model_key: str):
    """Тест одной легкой модели."""
    print(f"\n🚀 Тестирование {model_key}...")
    print("-" * 40)
    
    try:
        # Проверка кеша
        is_cached, cache_msg = ModelLoader.check_model_cache(model_key)
        print(f"Кеш: {cache_msg}")
        
        if not is_cached:
            print("⚠️ Модель не в кеше - пропускаем")
            return False
        
        # Загрузка модели
        start_time = time.time()
        model = ModelLoader.load_model(model_key)
        load_time = time.time() - start_time
        
        print(f"✅ Загружена за {load_time:.2f}с")
        print(f"   Тип: {type(model).__name__}")
        
        # Создание тестового изображения
        test_image = Image.new('RGB', (200, 100), color='white')
        
        # Тест обработки
        try:
            start_time = time.time()
            
            if hasattr(model, 'extract_text'):
                result = model.extract_text(test_image)
            elif hasattr(model, 'process_image'):
                result = model.process_image(test_image)
            else:
                result = model.chat(test_image, "Что на изображении?")
            
            process_time = time.time() - start_time
            print(f"✅ Обработка за {process_time:.2f}с")
            print(f"   Результат: {len(str(result))} символов")
            
        except Exception as e:
            print(f"⚠️ Ошибка обработки: {e}")
        
        # Выгрузка модели
        ModelLoader.unload_model(model_key)
        print("🔄 Модель выгружена")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Основная функция."""
    print("🧪 ТЕСТ ЛЕГКИХ МОДЕЛЕЙ ДЛЯ RTX 5070 Ti")
    print("=" * 60)
    
    # Легкие модели в порядке возрастания VRAM
    light_models = [
        "deepseek_ocr",      # 0.01GB
        "got_ocr_hf",        # 1.1GB
        "got_ocr_ucas",      # 2.7GB
        "qwen3_vl_2b",       # 4.4GB
        "qwen_vl_2b",        # 4.7GB
    ]
    
    print(f"Тестируем {len(light_models)} легких моделей:")
    for model in light_models:
        print(f"  • {model}")
    
    successful = []
    failed = []
    
    for model_key in light_models:
        success = test_light_model(model_key)
        if success:
            successful.append(model_key)
        else:
            failed.append(model_key)
    
    # Результаты
    print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"✅ Успешно: {len(successful)}")
    print(f"❌ Неудачно: {len(failed)}")
    
    if successful:
        print(f"\n✅ РАБОЧИЕ МОДЕЛИ:")
        for model in successful:
            print(f"   • {model}")
    
    if failed:
        print(f"\n❌ ПРОБЛЕМНЫЕ МОДЕЛИ:")
        for model in failed:
            print(f"   • {model}")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    if successful:
        print(f"   🚀 Для быстрого старта используйте: {successful[0]}")
        print(f"   ⚖️ Для баланса скорость/качество: {successful[-1] if len(successful) > 1 else successful[0]}")
    
    print(f"\n🎯 Для запуска интерфейса:")
    print(f"   streamlit run app.py")
    
    return len(successful) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)