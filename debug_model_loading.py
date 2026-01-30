#!/usr/bin/env python3
"""
Отладка загрузки модели - проверяем, какая модель действительно используется
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_model_loading():
    """Проверяем, какая модель загружается для dots_ocr."""
    
    print("🔍 Отладка загрузки модели dots_ocr")
    print("=" * 50)
    
    try:
        # Импортируем ModelLoader
        from models.model_loader import ModelLoader
        
        print("✅ ModelLoader импортирован успешно")
        
        # Проверяем registry
        registry = ModelLoader.MODEL_REGISTRY
        
        if "dots_ocr" in registry:
            model_class = registry["dots_ocr"]
            print(f"📋 Модель для 'dots_ocr': {model_class}")
            print(f"📁 Файл модели: {model_class.__module__}")
            print(f"🏷️ Класс модели: {model_class.__name__}")
        else:
            print("❌ 'dots_ocr' не найден в registry")
        
        print("\n📊 Полный registry:")
        for key, value in registry.items():
            if "dots" in key.lower():
                print(f"  {key}: {value.__name__} ({value.__module__})")
        
        print("\n🧪 Попытка создания модели...")
        
        # Пробуем создать модель
        config = {
            'model_path': 'rednote-hilab/dots.ocr',
            'precision': 'fp16',
            'flash_attention': False,
            'attention_implementation': 'eager'
        }
        
        model_instance = ModelLoader.create_model("dots_ocr", config)
        print(f"✅ Модель создана: {type(model_instance).__name__}")
        print(f"📁 Модуль: {type(model_instance).__module__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск отладки загрузки модели")
    print()
    
    success = debug_model_loading()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Отладка завершена успешно")
    else:
        print("❌ Обнаружены проблемы")
    print("=" * 50)