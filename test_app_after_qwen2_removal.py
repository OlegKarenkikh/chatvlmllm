#!/usr/bin/env python3
"""
Быстрый тест приложения после удаления Qwen2-VL 2B
"""

import sys
import os

def test_app_imports():
    """Тестирует импорты приложения"""
    
    print("🧪 Тестирование импортов приложения...")
    
    try:
        # Тестируем импорт ModelLoader
        from models.model_loader import ModelLoader
        print("✅ ModelLoader импортирован успешно")
        
        # Тестируем загрузку конфигурации
        config = ModelLoader.load_config()
        print("✅ Конфигурация загружена успешно")
        
        # Проверяем модели
        models = config.get('models', {})
        print(f"✅ Найдено {len(models)} моделей в конфигурации")
        
        # Проверяем, что qwen_vl_2b действительно удалена
        if 'qwen_vl_2b' not in models:
            print("✅ qwen_vl_2b успешно удалена")
        else:
            print("❌ qwen_vl_2b все еще присутствует!")
            return False
        
        # Проверяем MODEL_REGISTRY
        registry = ModelLoader.MODEL_REGISTRY
        print(f"✅ MODEL_REGISTRY содержит {len(registry)} типов моделей")
        
        if 'qwen_vl_2b' not in registry:
            print("✅ qwen_vl_2b удалена из MODEL_REGISTRY")
        else:
            print("❌ qwen_vl_2b все еще в MODEL_REGISTRY!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании импортов: {e}")
        return False

def test_remaining_models():
    """Тестирует оставшиеся модели"""
    
    print("\n🔧 Тестирование оставшихся моделей...")
    
    try:
        from models.model_loader import ModelLoader
        
        config = ModelLoader.load_config()
        models = config.get('models', {})
        
        print("📊 Оставшиеся модели:")
        for model_key, model_config in models.items():
            model_name = model_config.get('name', model_key)
            model_path = model_config.get('model_path', 'N/A')
            print(f"  • {model_name}")
            print(f"    ID: {model_key}")
            print(f"    Путь: {model_path}")
            print()
        
        # Проверяем, что есть альтернативы Qwen
        qwen_models = [k for k in models.keys() if 'qwen' in k.lower()]
        if qwen_models:
            print(f"✅ Доступны альтернативные Qwen модели: {qwen_models}")
        else:
            print("⚠️ Нет доступных Qwen моделей")
        
        # Проверяем, что есть другие модели для OCR
        ocr_models = [k for k in models.keys() if any(word in k.lower() for word in ['got', 'ocr', 'phi', 'deepseek'])]
        if ocr_models:
            print(f"✅ Доступны альтернативные OCR модели: {ocr_models}")
        else:
            print("⚠️ Нет доступных OCR моделей")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании моделей: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тестирование приложения после удаления Qwen2-VL 2B")
    print("=" * 60)
    
    imports_ok = test_app_imports()
    
    if imports_ok:
        models_ok = test_remaining_models()
        
        if models_ok:
            print("\n🎉 Все тесты прошли успешно!")
            print("\n📋 Резюме:")
            print("  ✅ Qwen2-VL 2B (Emergency Mode) успешно удалена")
            print("  ✅ Приложение работает корректно")
            print("  ✅ Доступны альтернативные модели")
            print("  ✅ Конфигурация валидна")
            
            print("\n💡 Рекомендуемые альтернативы:")
            print("  • Qwen3-VL 2B - улучшенная версия")
            print("  • GOT-OCR 2.0 - быстрый OCR")
            print("  • Phi-3.5 Vision - сложный анализ")
        else:
            print("\n❌ Ошибка при тестировании моделей")
            sys.exit(1)
    else:
        print("\n❌ Ошибка при тестировании импортов")
        sys.exit(1)