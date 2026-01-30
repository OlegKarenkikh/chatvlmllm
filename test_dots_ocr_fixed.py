#!/usr/bin/env python3
"""Тест исправленной модели dots.ocr."""

import sys
from pathlib import Path
from PIL import Image
import time

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def test_dots_ocr_fixed():
    """Тест исправленной модели dots.ocr."""
    print("🔧 ТЕСТ ИСПРАВЛЕННОЙ МОДЕЛИ DOTS.OCR")
    print("=" * 50)
    
    # Загрузка изображения
    try:
        image = Image.open("test_interface_image.png")
        print(f"✅ Изображение загружено: {image.size}, режим: {image.mode}")
    except:
        print("❌ Не найдено test_interface_image.png")
        return
    
    try:
        # Загрузка модели
        start_time = time.time()
        model = ModelLoader.load_model("dots_ocr")
        load_time = time.time() - start_time
        print(f"✅ Модель dots.ocr загружена за {load_time:.2f}с")
        
        # Тест простого OCR
        print(f"\n🧪 Тест простого OCR...")
        try:
            start_time = time.time()
            result = model.process_image(image, prompt="Extract all text from this image.", mode="ocr_only")
            process_time = time.time() - start_time
            
            print(f"✅ Успешная обработка за {process_time:.2f}с!")
            print(f"📊 Длина результата: {len(result)} символов")
            print(f"📄 Результат:")
            print("-" * 30)
            print(result)
            print("-" * 30)
            
            # Анализ качества
            if len(result) < 10:
                print("⚠️ Слишком короткий результат")
            elif "error" in result.lower():
                print("⚠️ Результат содержит ошибку")
            elif any(word in result.upper() for word in ["ВОДИТЕЛЬСКОЕ", "УДОСТОВЕРЕНИЕ", "ВАКАРИН"]):
                print("✅ Результат содержит ожидаемые слова!")
            else:
                print("🤔 Результат выглядит необычно")
            
        except Exception as e:
            print(f"❌ Ошибка обработки: {e}")
        
        # Тест чата
        print(f"\n💬 Тест чата...")
        try:
            start_time = time.time()
            result = model.chat(image, "Что написано в этом документе?")
            process_time = time.time() - start_time
            
            print(f"✅ Чат работает за {process_time:.2f}с!")
            print(f"📊 Длина ответа: {len(result)} символов")
            print(f"📄 Ответ: {result[:200]}...")
            
        except Exception as e:
            print(f"❌ Ошибка чата: {e}")
        
        # Выгрузка
        ModelLoader.unload_model("dots_ocr")
        print(f"\n🔄 Модель выгружена")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")


def compare_all_models():
    """Сравнение всех рабочих моделей."""
    print(f"\n📊 СРАВНЕНИЕ ВСЕХ РАБОЧИХ МОДЕЛЕЙ")
    print("=" * 60)
    
    # Загрузка изображения
    try:
        image = Image.open("test_interface_image.png")
        print(f"✅ Изображение загружено: {image.size}")
    except:
        print("❌ Не найдено test_interface_image.png")
        return
    
    models_to_test = [
        ("qwen_vl_2b", "Qwen2-VL 2B"),
        ("qwen3_vl_2b", "Qwen3-VL 2B"), 
        ("got_ocr_hf", "GOT-OCR HF"),
        ("dots_ocr", "dots.ocr")
    ]
    
    results = {}
    
    for model_key, model_name in models_to_test:
        print(f"\n🚀 Тест {model_name}...")
        print("-" * 30)
        
        try:
            # Загрузка
            start_time = time.time()
            model = ModelLoader.load_model(model_key)
            load_time = time.time() - start_time
            
            # Обработка
            start_time = time.time()
            
            if hasattr(model, 'extract_text'):
                text = model.extract_text(image)
            elif hasattr(model, 'process_image'):
                text = model.process_image(image)
            else:
                text = model.chat(image, "Извлеките весь текст из этого документа.")
            
            process_time = time.time() - start_time
            
            # Оценка качества
            quality = "Неизвестно"
            if len(text) < 10:
                quality = "Плохо (короткий)"
            elif "error" in text.lower():
                quality = "Ошибка"
            elif any(word in text.upper() for word in ["ВОДИТЕЛЬСКОЕ", "УДОСТОВЕРЕНИЕ"]):
                quality = "Отлично (читаемый)"
            elif any(char in text for char in "BOJNTEJBCKOEVJOCTOBEPENNE"):
                quality = "Плохо (искаженный)"
            else:
                quality = "Средне"
            
            results[model_key] = {
                "name": model_name,
                "load_time": load_time,
                "process_time": process_time,
                "text_length": len(text),
                "quality": quality,
                "text_preview": text[:50] + "..." if len(text) > 50 else text
            }
            
            print(f"✅ Загрузка: {load_time:.2f}с, Обработка: {process_time:.2f}с")
            print(f"📊 Длина: {len(text)}, Качество: {quality}")
            print(f"📄 Превью: {text[:50]}...")
            
            # Выгрузка
            ModelLoader.unload_model(model_key)
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            results[model_key] = {
                "name": model_name,
                "error": str(e),
                "quality": "Ошибка"
            }
    
    # Итоговая таблица
    print(f"\n📈 ИТОГОВАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("=" * 80)
    print(f"{'Модель':<20} {'Загрузка':<10} {'Обработка':<10} {'Длина':<8} {'Качество':<15}")
    print("-" * 80)
    
    for model_key, result in results.items():
        if "error" in result:
            print(f"{result['name']:<20} {'ERROR':<10} {'ERROR':<10} {'ERROR':<8} {result['quality']:<15}")
        else:
            print(f"{result['name']:<20} {result['load_time']:<10.2f} {result['process_time']:<10.2f} {result['text_length']:<8} {result['quality']:<15}")
    
    # Рекомендации
    print(f"\n🎯 РЕКОМЕНДАЦИИ:")
    best_models = [k for k, v in results.items() if v.get('quality') == 'Отлично (читаемый)']
    if best_models:
        print(f"✅ Лучшие модели: {', '.join([results[k]['name'] for k in best_models])}")
    else:
        print(f"⚠️ Нет моделей с отличным качеством")


if __name__ == "__main__":
    test_dots_ocr_fixed()
    compare_all_models()