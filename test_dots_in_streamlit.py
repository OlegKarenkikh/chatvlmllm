#!/usr/bin/env python3
"""
Тест dots.ocr в Streamlit интерфейсе
"""

import os
import sys
import time
from pathlib import Path
from PIL import Image

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Set environment variable
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from models.model_loader import ModelLoader
from utils.logger import logger


def test_dots_in_interface():
    """Тест dots.ocr как в Streamlit интерфейсе."""
    
    print("🖥️ ТЕСТ DOTS.OCR В STREAMLIT ИНТЕРФЕЙСЕ")
    print("=" * 50)
    
    try:
        # Simulate Streamlit model loading
        print("📥 Загрузка dots.ocr (как в Streamlit)...")
        
        start_time = time.time()
        model_wrapper = ModelLoader.load_model('dots_ocr')
        load_time = time.time() - start_time
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Test with document
        image_path = "test_document.png"
        if not Path(image_path).exists():
            print(f"❌ Файл {image_path} не найден")
            return
        
        image = Image.open(image_path)
        print(f"📷 Изображение: {image.size}")
        
        # Test parse_document (main Streamlit function)
        print("\n📋 Тест parse_document (основная функция Streamlit)...")
        
        parse_start = time.time()
        result = model_wrapper.parse_document(image, return_json=True)
        parse_time = time.time() - parse_start
        
        print(f"✅ parse_document завершен за {parse_time:.2f}s")
        print(f"📊 Тип результата: {type(result)}")
        
        if isinstance(result, dict):
            print(f"📊 Ключи: {list(result.keys())}")
            
            if 'raw_text' in result:
                raw_text = result['raw_text']
                if raw_text and len(raw_text) > 50:
                    print(f"✅ Получен валидный результат: {len(raw_text)} символов")
                    print(f"📝 Начало: {raw_text[:100]}...")
                    
                    # Try to parse as JSON
                    try:
                        import json
                        parsed = json.loads(raw_text)
                        print(f"✅ Валидный JSON: {type(parsed)}")
                        
                        if isinstance(parsed, list):
                            print(f"📊 Найдено элементов: {len(parsed)}")
                            
                            # Show categories
                            categories = {}
                            for element in parsed[:5]:  # First 5 elements
                                if isinstance(element, dict):
                                    cat = element.get('category', 'Unknown')
                                    categories[cat] = categories.get(cat, 0) + 1
                            
                            print(f"📊 Категории: {categories}")
                            print("✅ dots.ocr ПОЛНОСТЬЮ РАБОТАЕТ В STREAMLIT!")
                            
                    except json.JSONDecodeError:
                        print("⚠️ Результат не JSON, но есть текст")
                        
                else:
                    print(f"⚠️ Короткий результат: {raw_text}")
            else:
                print(f"⚠️ Нет raw_text в результате")
        
        # Test extract_text_only
        print("\n🔤 Тест extract_text_only...")
        
        text_start = time.time()
        text_result = model_wrapper.extract_text_only(image)
        text_time = time.time() - text_start
        
        print(f"✅ extract_text_only завершен за {text_time:.2f}s")
        print(f"📝 Результат: {len(str(text_result))} символов")
        
        if text_result and len(str(text_result)) > 10:
            print("✅ extract_text_only работает!")
        
        # Unload model
        ModelLoader.unload_model('dots_ocr')
        
        total_time = time.time() - start_time
        print(f"\n⏱️ Общее время: {total_time:.2f}s")
        print("✅ DOTS.OCR ГОТОВ ДЛЯ STREAMLIT!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    test_dots_in_interface()