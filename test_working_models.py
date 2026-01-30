#!/usr/bin/env python3
"""Быстрый тест рабочих моделей."""

import sys
from pathlib import Path

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def test_working_models():
    """Тест моделей, которые должны работать."""
    working_models = [
        "qwen_vl_2b",
        "qwen3_vl_2b", 
        "got_ocr_hf",
        "dots_ocr",
        "phi3_vision",
        "got_ocr_ucas"
    ]
    
    print("🧪 Тестирование рабочих моделей")
    print("=" * 50)
    
    for model_key in working_models:
        print(f"\n🚀 Тестирование {model_key}...")
        try:
            # Проверить кеш
            is_cached, msg = ModelLoader.check_model_cache(model_key)
            if not is_cached:
                print(f"   ❌ Не кеширована: {msg}")
                continue
                
            # Загрузить модель
            model = ModelLoader.load_model(model_key)
            print(f"   ✅ Загружена успешно: {type(model).__name__}")
            
            # Выгрузить
            ModelLoader.unload_model(model_key)
            print(f"   🔄 Выгружена")
            
        except Exception as e:
            print(f"   ❌ Неудача: {e}")
    
    print(f"\n✅ Тест завершен!")


if __name__ == "__main__":
    test_working_models()