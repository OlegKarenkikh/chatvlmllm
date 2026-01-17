#!/usr/bin/env python3
"""Отладка интерфейса OCR."""

import sys
from pathlib import Path
from PIL import Image

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def debug_interface_ocr():
    """Отладка OCR как в интерфейсе."""
    print("🔍 ОТЛАДКА ИНТЕРФЕЙСА OCR")
    print("=" * 40)
    
    # Загрузка тестового изображения (как в интерфейсе)
    try:
        image = Image.open("test_interface_image.png")
        print("✅ Изображение загружено")
    except:
        print("❌ Не найдено test_interface_image.png")
        return
    
    # Тест модели got_ocr_hf (как в интерфейсе)
    selected_model = "got_ocr_hf"
    
    try:
        print(f"\n🚀 Загрузка модели {selected_model}...")
        model = ModelLoader.load_model(selected_model)
        print("✅ Модель загружена")
        
        print(f"\n🔍 Проверка методов модели:")
        print(f"   hasattr(model, 'extract_text'): {hasattr(model, 'extract_text')}")
        print(f"   hasattr(model, 'process_image'): {hasattr(model, 'process_image')}")
        print(f"   hasattr(model, 'chat'): {hasattr(model, 'chat')}")
        
        # Обработка изображения (точно как в интерфейсе)
        print(f"\n🔄 Обработка изображения...")
        
        if hasattr(model, 'extract_text'):
            print("   Используем extract_text")
            text = model.extract_text(image)
        elif hasattr(model, 'process_image'):
            print("   Используем process_image")
            text = model.process_image(image)
        else:
            print("   Используем chat")
            text = model.chat(image, "Извлеките весь текст из этого документа, сохраняя структуру и форматирование.")
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"   Тип: {type(text)}")
        print(f"   Длина: {len(text)} символов")
        print(f"   Содержимое:")
        print("-" * 40)
        print(repr(text))  # Показать с escape символами
        print("-" * 40)
        print(text)  # Показать как есть
        print("-" * 40)
        
        # Проверка на пустоту или проблемы
        if not text or text.strip() == "":
            print("❌ ПРОБЛЕМА: Пустой результат!")
        elif len(text.strip()) < 10:
            print("⚠️ ПРОБЛЕМА: Слишком короткий результат!")
        elif "RUS" in text and len(text) < 20:
            print("⚠️ ПРОБЛЕМА: Результат содержит только 'RUS'!")
        else:
            print("✅ Результат выглядит нормально")
        
        # Выгрузка
        ModelLoader.unload_model(selected_model)
        print("\n🔄 Модель выгружена")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_interface_ocr()