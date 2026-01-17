#!/usr/bin/env python3
"""Тест OCR в интерфейсе с реальным изображением."""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import time

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def create_test_image():
    """Создать тестовое изображение документа."""
    # Создаем изображение как в интерфейсе
    width, height = 600, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Пытаемся использовать системный шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        title_font = ImageFont.truetype("arial.ttf", 28)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
            title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ", fill='black', font=title_font)
    
    # Основной текст
    text_lines = [
        "1. ВАКАРИНЦЕВ",
        "2. АНДРЕЙ ПАВЛОВИЧ", 
        "3. 13.09.1995",
        "4a) 03.01.2014  4b) 03.01.2024",
        "4c) ГИБДД 2747",
        "5. 0166860",
        "8. АЛТАЙСКИЙ КРАЙ"
    ]
    
    y_pos = 80
    for line in text_lines:
        draw.text((50, y_pos), line, fill='black', font=font)
        y_pos += 30
    
    # Добавляем рамку
    draw.rectangle([20, 20, width-20, height-20], outline='black', width=2)
    
    return image


def test_interface_ocr():
    """Тест OCR как в интерфейсе."""
    print("🧪 ТЕСТ OCR ИНТЕРФЕЙСА")
    print("=" * 40)
    
    # Создание тестового изображения
    print("📄 Создание тестового изображения...")
    image = create_test_image()
    image.save("test_interface_image.png")
    print("✅ Изображение создано: test_interface_image.png")
    
    # Тест рабочих моделей
    working_models = ["got_ocr_hf", "qwen_vl_2b", "qwen3_vl_2b"]
    
    results = {}
    
    for model_key in working_models:
        print(f"\n🚀 Тест модели {model_key}...")
        
        try:
            # Загрузка модели (как в интерфейсе)
            start_time = time.time()
            model = ModelLoader.load_model(model_key)
            load_time = time.time() - start_time
            
            print(f"✅ Модель загружена за {load_time:.2f}с")
            
            # Обработка изображения (как в интерфейсе)
            start_time = time.time()
            
            if hasattr(model, 'extract_text'):
                # Для моделей с методом extract_text (Qwen3-VL)
                text = model.extract_text(image)
            elif hasattr(model, 'process_image'):
                # Для OCR моделей (GOT-OCR, dots.ocr)
                text = model.process_image(image)
            else:
                # Для общих VLM моделей
                text = model.chat(image, "Извлеките весь текст из этого документа, сохраняя структуру и форматирование.")
            
            process_time = time.time() - start_time
            
            print(f"✅ Обработка за {process_time:.2f}с")
            print(f"📊 Результат ({len(text)} символов):")
            print("-" * 30)
            print(text[:200] + "..." if len(text) > 200 else text)
            print("-" * 30)
            
            # Вычисление уверенности (как в интерфейсе)
            confidence = min(0.95, max(0.7, len(text.strip()) / 100))
            
            results[model_key] = {
                "success": True,
                "text": text,
                "confidence": confidence,
                "load_time": load_time,
                "process_time": process_time
            }
            
            # Выгрузка модели
            ModelLoader.unload_model(model_key)
            print("🔄 Модель выгружена")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            results[model_key] = {
                "success": False,
                "error": str(e)
            }
    
    # Итоги
    print(f"\n📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 40)
    
    successful = [k for k, v in results.items() if v.get("success", False)]
    failed = [k for k, v in results.items() if not v.get("success", False)]
    
    print(f"✅ Успешно: {len(successful)}")
    print(f"❌ Неудачно: {len(failed)}")
    
    if successful:
        print(f"\n✅ РАБОЧИЕ В ИНТЕРФЕЙСЕ:")
        for model in successful:
            result = results[model]
            print(f"   • {model}: {result['process_time']:.2f}с, {len(result['text'])} символов")
    
    if failed:
        print(f"\n❌ ПРОБЛЕМНЫЕ В ИНТЕРФЕЙСЕ:")
        for model in failed:
            print(f"   • {model}: {results[model]['error']}")
    
    # Рекомендации
    if successful:
        fastest = min(successful, key=lambda x: results[x]['process_time'])
        most_text = max(successful, key=lambda x: len(results[x]['text']))
        
        print(f"\n💡 РЕКОМЕНДАЦИИ ДЛЯ ИНТЕРФЕЙСА:")
        print(f"   🚀 Самая быстрая: {fastest} ({results[fastest]['process_time']:.2f}с)")
        print(f"   📄 Больше всего текста: {most_text} ({len(results[most_text]['text'])} символов)")
    
    return len(successful) > 0


if __name__ == "__main__":
    success = test_interface_ocr()
    sys.exit(0 if success else 1)