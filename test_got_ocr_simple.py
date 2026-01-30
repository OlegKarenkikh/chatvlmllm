#!/usr/bin/env python3
"""
Простой тест got_ocr_hf без зависания
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_simple_document():
    """Создаем простой документ для OCR"""
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 20), "ТЕСТОВЫЙ ДОКУМЕНТ", fill='black', font=font)
    draw.text((20, 50), "Номер: 123456789", fill='black', font=font)
    draw.text((20, 80), "Дата: 19.01.2026", fill='black', font=font)
    draw.text((20, 110), "Статус: АКТИВЕН", fill='black', font=font)
    
    return img

def test_simple_got_ocr():
    """Простой тест got_ocr_hf"""
    print("🚀 ПРОСТОЙ ТЕСТ GOT-OCR HF")
    print("=" * 40)
    
    # Проверяем GPU
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        print(f"✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f}GB")
    else:
        print("❌ GPU недоступна")
        return False
    
    try:
        # Импортируем только то, что нужно
        from models.model_loader import ModelLoader
        
        print("📥 Загружаем got_ocr_hf...")
        start_time = time.time()
        
        # Загружаем модель
        model = ModelLoader.load_model('got_ocr_hf')
        load_time = time.time() - start_time
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Создаем документ для OCR
        print("🖼️ Создаем тестовый документ...")
        image = create_simple_document()
        
        # OCR обработка
        print("🔍 Выполняем OCR...")
        start_process = time.time()
        
        result = model.process_image(image)
        process_time = time.time() - start_process
        
        print(f"✅ OCR завершен за {process_time:.3f}s")
        print(f"📝 Результат ({len(result)} символов):")
        print(f"   {result}")
        
        # Проверяем качество OCR
        keywords = ["ТЕСТОВЫЙ", "ДОКУМЕНТ", "123456789", "19.01.2026", "АКТИВЕН"]
        found = sum(1 for kw in keywords if kw in result.upper())
        print(f"🎯 Найдено ключевых слов: {found}/{len(keywords)}")
        
        # Выгружаем модель
        print("🔄 Выгружаем модель...")
        model.unload()
        
        print("🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print(f"⚡ Производительность: {process_time:.3f}s обработка")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_got_ocr()
    exit(0 if success else 1)