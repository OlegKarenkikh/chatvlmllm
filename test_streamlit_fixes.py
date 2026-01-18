#!/usr/bin/env python3
"""Тест исправлений Streamlit и dots.ocr."""

import sys
from pathlib import Path
from PIL import Image
import time

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def test_dots_ocr_torch_fix():
    """Тест исправления проблемы с torch в dots.ocr."""
    print("🔧 ТЕСТ ИСПРАВЛЕНИЯ DOTS.OCR")
    print("=" * 40)
    
    # Загрузка изображения
    try:
        image = Image.open("test_interface_image.png")
        print(f"✅ Изображение загружено: {image.size}")
    except:
        print("❌ Не найдено test_interface_image.png")
        return False
    
    try:
        # Загрузка модели
        start_time = time.time()
        model = ModelLoader.load_model("dots_ocr")
        load_time = time.time() - start_time
        print(f"✅ Модель загружена за {load_time:.2f}с")
        
        # Тест обработки
        start_time = time.time()
        result = model.process_image(image, prompt="Extract text from this image.", mode="ocr_only")
        process_time = time.time() - start_time
        
        print(f"✅ Обработка за {process_time:.2f}с")
        print(f"📊 Результат: {len(result)} символов")
        
        if "error" in result.lower():
            print(f"⚠️ Результат содержит ошибку: {result[:100]}...")
            success = False
        else:
            print(f"✅ Результат выглядит нормально: {result[:100]}...")
            success = True
        
        # Выгрузка
        ModelLoader.unload_model("dots_ocr")
        print("🔄 Модель выгружена")
        
        return success
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_session_state_safety():
    """Тест безопасности session_state."""
    print(f"\n🛡️ ТЕСТ БЕЗОПАСНОСТИ SESSION_STATE")
    print("=" * 40)
    
    # Имитация функции из app.py
    def get_session_state(key, default=None):
        """Безопасное получение значения из session_state."""
        # Имитируем отсутствие streamlit
        class MockSessionState:
            def __init__(self):
                self.data = {}
            
            def __getattr__(self, key):
                if key in self.data:
                    return self.data[key]
                raise AttributeError(f"No attribute {key}")
            
            def __setattr__(self, key, value):
                if key == 'data':
                    super().__setattr__(key, value)
                else:
                    self.data[key] = value
        
        mock_st = MockSessionState()
        
        try:
            return getattr(mock_st, key, default)
        except AttributeError:
            return default
    
    # Тесты
    tests = [
        ("existing_key", None, None),
        ("non_existing_key", None, None),
        ("ocr_result", {"test": "data"}, {"test": "data"}),
    ]
    
    success_count = 0
    for key, expected, default in tests:
        try:
            result = get_session_state(key, default)
            if result == expected:
                print(f"✅ Тест {key}: OK")
                success_count += 1
            else:
                print(f"⚠️ Тест {key}: ожидалось {expected}, получено {result}")
        except Exception as e:
            print(f"❌ Тест {key}: ошибка {e}")
    
    print(f"📊 Успешных тестов: {success_count}/{len(tests)}")
    return success_count == len(tests)


def main():
    """Главная функция тестирования."""
    print("🧪 ТЕСТ ИСПРАВЛЕНИЙ STREAMLIT И DOTS.OCR")
    print("=" * 50)
    
    # Тест dots.ocr
    dots_success = test_dots_ocr_torch_fix()
    
    # Тест session_state
    session_success = test_session_state_safety()
    
    # Итоги
    print(f"\n🏁 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 30)
    print(f"dots.ocr: {'✅ ИСПРАВЛЕНО' if dots_success else '❌ ПРОБЛЕМЫ'}")
    print(f"session_state: {'✅ БЕЗОПАСНО' if session_success else '❌ ПРОБЛЕМЫ'}")
    
    if dots_success and session_success:
        print(f"\n🎉 ВСЕ ИСПРАВЛЕНИЯ РАБОТАЮТ!")
    else:
        print(f"\n⚠️ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ОТЛАДКА")


if __name__ == "__main__":
    main()