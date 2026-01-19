#!/usr/bin/env python3
"""
Быстрый тест интерфейса - проверяем вывод моделей
"""

import time
from PIL import Image, ImageDraw, ImageFont
from models.model_loader import ModelLoader
from utils.logger import logger

def create_test_image():
    """Создаем простое тестовое изображение"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 20), "ТЕСТОВЫЙ ДОКУМЕНТ", fill='black', font=font)
    draw.text((20, 60), "Номер: 123456789", fill='black', font=font)
    draw.text((20, 100), "Дата: 19.01.2026", fill='black', font=font)
    draw.text((20, 140), "Статус: АКТИВЕН", fill='black', font=font)
    
    img.save("test_quick.png")
    return img

def test_model_output():
    """Тестируем вывод модели"""
    print("🔍 ТЕСТ ВЫВОДА МОДЕЛЕЙ")
    print("=" * 40)
    
    # Создаем тестовое изображение
    print("📸 Создаем тестовое изображение...")
    image = create_test_image()
    
    # Тестируем qwen_vl_2b (быстрая модель)
    print("\n🚀 Тестируем qwen_vl_2b...")
    try:
        start_time = time.time()
        model = ModelLoader.load_model('qwen_vl_2b')
        load_time = time.time() - start_time
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Обработка изображения
        start_process = time.time()
        result = model.process_image(image, "Извлеки весь текст из этого изображения")
        process_time = time.time() - start_process
        
        print(f"✅ Обработка завершена за {process_time:.2f}s")
        print(f"📝 РЕЗУЛЬТАТ ({len(result)} символов):")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # Проверяем, что результат не пустой
        if result and len(result.strip()) > 0:
            print("✅ МОДЕЛЬ ВЫДАЕТ РЕЗУЛЬТАТ!")
        else:
            print("❌ МОДЕЛЬ НЕ ВЫДАЕТ РЕЗУЛЬТАТ!")
        
        model.unload()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("🎯 ТЕСТ ЗАВЕРШЕН")

if __name__ == "__main__":
    test_model_output()