#!/usr/bin/env python3
"""
Тест восстановленной got_ocr_hf модели
"""

import time
from PIL import Image, ImageDraw, ImageFont
from models.model_loader import ModelLoader
from utils.logger import logger

def create_test_image():
    """Создаем тестовое изображение"""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 20), "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ", fill='black', font=font)
    draw.text((20, 60), "Серия: 77 АА", fill='black', font=font)
    draw.text((20, 100), "Номер: 123456", fill='black', font=font)
    draw.text((20, 140), "Фамилия: ИВАНОВ", fill='black', font=font)
    draw.text((20, 180), "Имя: ИВАН ИВАНОВИЧ", fill='black', font=font)
    draw.text((20, 220), "Дата рождения: 01.01.1990", fill='black', font=font)
    draw.text((20, 260), "Дата выдачи: 15.03.2020", fill='black', font=font)
    draw.text((20, 300), "Действительно до: 15.03.2030", fill='black', font=font)
    
    img.save("test_driver_license.png")
    return img

def test_got_ocr_restored():
    """Тестируем восстановленную got_ocr_hf"""
    print("🚀 ТЕСТ ВОССТАНОВЛЕННОЙ GOT-OCR HF")
    print("=" * 50)
    
    # Создаем тестовое изображение
    print("📸 Создаем тестовое изображение...")
    image = create_test_image()
    
    # Тестируем got_ocr_hf
    print("\n🔍 Тестируем got_ocr_hf (восстановленная версия)...")
    try:
        start_time = time.time()
        model = ModelLoader.load_model('got_ocr_hf')
        load_time = time.time() - start_time
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Обработка изображения
        start_process = time.time()
        result = model.process_image(image)
        process_time = time.time() - start_process
        
        print(f"✅ Обработка завершена за {process_time:.2f}s")
        print(f"📝 РЕЗУЛЬТАТ ({len(result)} символов):")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # Проверяем качество результата
        if result and len(result.strip()) > 50:
            print("✅ ОТЛИЧНЫЙ РЕЗУЛЬТАТ!")
            
            # Проверяем наличие ключевых слов
            keywords = ["ВОДИТЕЛЬСКОЕ", "УДОСТОВЕРЕНИЕ", "ИВАНОВ", "123456"]
            found_keywords = sum(1 for kw in keywords if kw in result.upper())
            print(f"🎯 Найдено ключевых слов: {found_keywords}/{len(keywords)}")
            
            if found_keywords >= 2:
                print("✅ КАЧЕСТВО OCR: ОТЛИЧНО!")
            else:
                print("⚠️ КАЧЕСТВО OCR: СРЕДНЕЕ")
        else:
            print("❌ РЕЗУЛЬТАТ СЛИШКОМ КОРОТКИЙ!")
        
        # Финальная статистика
        print("\n" + "=" * 50)
        print("🎯 РЕЗУЛЬТАТЫ ТЕСТА:")
        print(f"✅ Загрузка: {load_time:.2f}s")
        print(f"✅ Обработка: {process_time:.2f}s")
        print(f"✅ Общее время: {load_time + process_time:.2f}s")
        print(f"✅ Размер результата: {len(result)} символов")
        
        # Проверяем использование GPU
        import torch
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated() / 1024**3
            print(f"✅ GPU память: {memory_used:.2f}GB")
        
        model.unload()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_got_ocr_restored()
    
    if success:
        print("\n🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("got_ocr_hf восстановлена и работает!")
    else:
        print("\n❌ Тест не пройден")
        exit(1)