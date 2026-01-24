#!/usr/bin/env python3
"""
Быстрый тест dots.ocr с улучшенными изображениями
"""

import sys
import os
import torch
from PIL import Image
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.dots_ocr_chatvlm_integration import DotsOCRChatVLM, initialize_dots_ocr

def quick_test():
    """Быстрый тест с простыми изображениями"""
    print("🧪 БЫСТРЫЙ ТЕСТ DOTS.OCR")
    print("=" * 40)
    
    # Инициализация
    if not initialize_dots_ocr():
        print("❌ Не удалось загрузить dots.ocr")
        return False
    
    dots_ocr = DotsOCRChatVLM()
    dots_ocr.load_model()
    
    # Тест с простым изображением
    test_images = [
        ("simple_test.png", "HELLO WORLD 123"),
        ("clear_test_document.png", "ТЕСТОВЫЙ ДОКУМЕНТ")
    ]
    
    for image_path, expected in test_images:
        if not os.path.exists(image_path):
            print(f"⚠️ Файл {image_path} не найден")
            continue
            
        print(f"\n🔍 Тестируем: {image_path}")
        print(f"🎯 Ожидаем: {expected}")
        
        # Загружаем изображение
        image = Image.open(image_path).convert('RGB')
        
        # Обрабатываем
        start_time = time.time()
        result = dots_ocr.process_image(image, "Extract all text from this image")
        end_time = time.time()
        
        print(f"⏱️ Время: {end_time - start_time:.3f}s")
        
        if result:
            print(f"📝 Результат: {result[:200]}...")
            
            # Проверяем, есть ли ожидаемый текст
            if expected.lower() in result.lower():
                print("✅ Ожидаемый текст найден!")
            else:
                print("⚠️ Ожидаемый текст не найден")
        else:
            print("❌ Пустой результат")
    
    # Очистка
    dots_ocr.cleanup()

if __name__ == "__main__":
    quick_test()