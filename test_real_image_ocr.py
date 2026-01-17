#!/usr/bin/env python3
"""Тест OCR с реальным изображением из интерфейса."""

import sys
from pathlib import Path
from PIL import Image
import time

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def test_all_models_with_real_image():
    """Тест всех моделей с реальным изображением."""
    print("🧪 ТЕСТ ВСЕХ МОДЕЛЕЙ С РЕАЛЬНЫМ ИЗОБРАЖЕНИЕМ")
    print("=" * 60)
    
    # Попробуем найти реальное изображение
    image_files = ["prava_obr-1.jpg", "test_real_image.png", "test_interface_image.png"]
    image = None
    image_path = None
    
    for file_path in image_files:
        if Path(file_path).exists():
            try:
                image = Image.open(file_path)
                image_path = file_path
                print(f"✅ Загружено изображение: {file_path}")
                break
            except Exception as e:
                print(f"⚠️ Ошибка загрузки {file_path}: {e}")
    
    if image is None:
        print("❌ Не найдено подходящее изображение")
        return
    
    print(f"📊 Размер изображения: {image.size}")
    print(f"📊 Режим: {image.mode}")
    
    # Тест всех рабочих моделей
    models_to_test = ["got_ocr_hf", "qwen_vl_2b", "qwen3_vl_2b"]
    
    results = {}
    
    for model_key in models_to_test:
        print(f"\n🚀 Тест модели {model_key}...")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Загрузка модели
            model = ModelLoader.load_model(model_key)
            load_time = time.time() - start_time
            print(f"✅ Модель загружена за {load_time:.2f}с")
            
            # Обработка изображения
            start_time = time.time()
            
            if hasattr(model, 'extract_text'):
                text = model.extract_text(image)
            elif hasattr(model, 'process_image'):
                text = model.process_image(image)
            else:
                text = model.chat(image, "Извлеките весь текст из этого документа, сохраняя структуру и форматирование.")
            
            process_time = time.time() - start_time
            
            print(f"✅ Обработка за {process_time:.2f}с")
            print(f"📊 Результат: {len(text)} символов")
            
            # Показать первые 100 символов
            preview = text[:100] + "..." if len(text) > 100 else text
            print(f"📄 Превью: {repr(preview)}")
            
            # Анализ качества
            quality = "Хорошо"
            if len(text) < 20:
                quality = "Плохо (слишком короткий)"
            elif "RUS BO ANTE" in text or any(c in text for c in "ÀÁÂÃÄÅÆÇÈÉÊË"):
                quality = "Плохо (искаженный текст)"
            elif len([word for word in text.split() if len(word) > 2]) < 5:
                quality = "Средне (мало слов)"
            
            results[model_key] = {
                "text": text,
                "length": len(text),
                "load_time": load_time,
                "process_time": process_time,
                "quality": quality
            }
            
            print(f"🎯 Качество: {quality}")
            
            # Выгрузка модели
            ModelLoader.unload_model(model_key)
            print("🔄 Модель выгружена")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            results[model_key] = {
                "error": str(e),
                "quality": "Ошибка"
            }
    
    # Итоги
    print(f"\n📊 СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
    print("=" * 60)
    
    for model_key, result in results.items():
        if "error" in result:
            print(f"❌ {model_key}: {result['error']}")
        else:
            print(f"✅ {model_key}:")
            print(f"   Качество: {result['quality']}")
            print(f"   Длина: {result['length']} символов")
            print(f"   Время: {result['process_time']:.2f}с")
            print(f"   Превью: {result['text'][:50]}...")
    
    # Рекомендации
    best_model = None
    best_quality = None
    
    for model_key, result in results.items():
        if "error" not in result and result['quality'] == "Хорошо":
            if best_model is None or result['process_time'] < results[best_model]['process_time']:
                best_model = model_key
                best_quality = result
    
    if best_model:
        print(f"\n🏆 ЛУЧШАЯ МОДЕЛЬ: {best_model}")
        print(f"   Качество: {best_quality['quality']}")
        print(f"   Время: {best_quality['process_time']:.2f}с")
        print(f"   Результат: {best_quality['text'][:100]}...")
    else:
        print(f"\n⚠️ НЕТ ХОРОШИХ РЕЗУЛЬТАТОВ")
        print("   Возможные причины:")
        print("   - Плохое качество изображения")
        print("   - Неподходящий формат документа")
        print("   - Проблемы с моделями")


if __name__ == "__main__":
    test_all_models_with_real_image()