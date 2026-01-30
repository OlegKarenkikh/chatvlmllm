#!/usr/bin/env python3
"""
Тест реальной загрузки модели через ModelLoader
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_actual_loading():
    """Тестируем реальную загрузку модели."""
    
    print("🧪 Тест реальной загрузки модели dots_ocr")
    print("=" * 50)
    
    try:
        # Импортируем ModelLoader
        from models.model_loader import ModelLoader
        
        print(f"✅ ModelLoader импортирован: {ModelLoader}")
        print(f"📁 Класс: {ModelLoader.__name__}")
        
        # Проверяем registry
        registry = ModelLoader.MODEL_REGISTRY
        model_class = registry.get("dots_ocr")
        
        print(f"📋 Класс для dots_ocr: {model_class}")
        print(f"📁 Модуль: {model_class.__module__}")
        
        # Пробуем загрузить модель
        print("\n🔄 Попытка загрузки модели...")
        
        config = {
            'model_path': 'rednote-hilab/dots.ocr',
            'precision': 'fp16',
            'flash_attention': False,
            'attention_implementation': 'eager'
        }
        
        # Используем метод load_model
        model = ModelLoader.load_model("dots_ocr", config)
        
        print(f"✅ Модель загружена: {type(model)}")
        print(f"📁 Модуль модели: {type(model).__module__}")
        print(f"🏷️ Класс модели: {type(model).__name__}")
        
        # Проверяем, что это правильная модель
        if "video_processor_fixed" in type(model).__module__:
            print("🎉 ПРАВИЛЬНАЯ МОДЕЛЬ ЗАГРУЖЕНА!")
            return True
        else:
            print("❌ НЕПРАВИЛЬНАЯ МОДЕЛЬ!")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск теста загрузки модели")
    print()
    
    success = test_actual_loading()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ТЕСТ ПРОЙДЕН - ПРАВИЛЬНАЯ МОДЕЛЬ")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН - НЕПРАВИЛЬНАЯ МОДЕЛЬ")
    print("=" * 50)