#!/usr/bin/env python3
"""Тест проблемы Streamlit с результатами OCR."""

import sys
from pathlib import Path
from PIL import Image
import time

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def simulate_streamlit_processing():
    """Симуляция обработки как в Streamlit."""
    print("🧪 СИМУЛЯЦИЯ STREAMLIT ОБРАБОТКИ")
    print("=" * 50)
    
    # Создание изображения (как в интерфейсе)
    image = Image.new('RGB', (600, 400), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        title_font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Текст как на водительских правах
    draw.text((50, 30), "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ", fill='black', font=title_font)
    draw.text((50, 70), "1. ВАКАРИНЦЕВ", fill='black', font=font)
    draw.text((50, 95), "2. АНДРЕЙ ПАВЛОВИЧ", fill='black', font=font)
    draw.text((50, 120), "3. 13.09.1995", fill='black', font=font)
    draw.text((50, 145), "4а) 03.01.2014  4b) 03.01.2024", fill='black', font=font)
    draw.text((50, 170), "4c) ГИБДД 2747", fill='black', font=font)
    draw.text((50, 195), "5. 0166860", fill='black', font=font)
    draw.text((50, 220), "8. АЛТАЙСКИЙ КРАЙ", fill='black', font=font)
    
    print("✅ Изображение создано")
    
    # Симуляция выбора модели (как в интерфейсе)
    selected_model = "got_ocr_hf"
    
    try:
        print(f"\n🚀 Загрузка модели {selected_model}...")
        start_time = time.time()
        
        # Загрузка выбранной модели (как в интерфейсе)
        model = ModelLoader.load_model(selected_model)
        
        # Обработка изображения (ТОЧНО как в интерфейсе)
        if hasattr(model, 'extract_text'):
            # Для моделей с методом extract_text (Qwen3-VL)
            print("   Используем extract_text")
            text = model.extract_text(image)
        elif hasattr(model, 'process_image'):
            # Для OCR моделей (GOT-OCR, dots.ocr)
            print("   Используем process_image")
            text = model.process_image(image)
        else:
            # Для общих VLM моделей
            print("   Используем chat")
            text = model.chat(image, "Извлеките весь текст из этого документа, сохраняя структуру и форматирование.")
        
        processing_time = time.time() - start_time
        
        print(f"✅ Обработка завершена за {processing_time:.2f}с")
        
        # ОТЛАДКА: Показать что получили (как в интерфейсе)
        print(f"\n🔍 ОТЛАДКА: Получен текст длиной {len(text)} символов")
        print(f"🔍 Первые 100 символов: {repr(text[:100])}")
        
        # Вычисление уверенности (как в интерфейсе)
        confidence = min(0.95, max(0.7, len(text.strip()) / 100))
        
        # Создание результата (как в интерфейсе)
        ocr_result = {
            "text": text,
            "confidence": confidence,
            "processing_time": processing_time,
            "model_used": selected_model
        }
        
        print(f"\n📊 РЕЗУЛЬТАТ STREAMLIT:")
        print(f"   text: {len(ocr_result['text'])} символов")
        print(f"   confidence: {ocr_result['confidence']:.1%}")
        print(f"   processing_time: {ocr_result['processing_time']:.2f}с")
        print(f"   model_used: {ocr_result['model_used']}")
        
        print(f"\n📄 ПОЛНЫЙ ТЕКСТ:")
        print("=" * 50)
        print(repr(ocr_result["text"]))
        print("=" * 50)
        print(ocr_result["text"])
        print("=" * 50)
        
        # Проверка на проблемы
        if not ocr_result["text"] or ocr_result["text"].strip() == "":
            print("❌ ПРОБЛЕМА: Пустой результат!")
        elif len(ocr_result["text"].strip()) < 10:
            print("⚠️ ПРОБЛЕМА: Слишком короткий результат!")
        elif "RUS" in ocr_result["text"] and len(ocr_result["text"]) < 20:
            print("⚠️ ПРОБЛЕМА: Результат содержит только 'RUS'!")
        else:
            print("✅ Результат выглядит нормально для Streamlit")
        
        # Выгрузка
        ModelLoader.unload_model(selected_model)
        print("\n🔄 Модель выгружена")
        
        return ocr_result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = simulate_streamlit_processing()
    if result:
        print(f"\n🎯 ИТОГ: Результат готов для Streamlit с {len(result['text'])} символами")
    else:
        print(f"\n❌ ИТОГ: Ошибка в обработке")