#!/usr/bin/env python3
"""
Простой тест одной модели после исправлений
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_simple_document():
    """Создаем простой документ"""
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 20), "ТЕСТ ИСПРАВЛЕНИЙ", fill='black', font=font)
    draw.text((20, 50), "Модель: qwen3_vl_2b", fill='black', font=font)
    draw.text((20, 80), "Precision: fp16", fill='black', font=font)
    draw.text((20, 110), "Flash Attention: OFF", fill='black', font=font)
    draw.text((20, 140), "Статус: ИСПРАВЛЕНО", fill='black', font=font)
    
    return img

def test_single_model():
    """Тестирует одну модель"""
    print("🔧 ТЕСТ ИСПРАВЛЕНИЙ МОДЕЛИ")
    print("=" * 40)
    
    # Очищаем GPU память
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gpu_name = torch.cuda.get_device_name(0)
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        vram_allocated = torch.cuda.memory_allocated(0) / 1024**3
        print(f"✅ GPU: {gpu_name}")
        print(f"✅ VRAM: {vram_allocated:.2f}GB / {vram_total:.2f}GB")
    
    try:
        from models.model_loader import ModelLoader
        
        # Тестируем qwen3_vl_2b (она работала в API)
        model_name = "qwen3_vl_2b"
        
        print(f"\n📥 Загружаем {model_name}...")
        start_load = time.time()
        
        model = ModelLoader.load_model(model_name)
        load_time = time.time() - start_load
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Проверяем VRAM
        if torch.cuda.is_available():
            vram_used = torch.cuda.memory_allocated(0) / 1024**3
            print(f"💾 VRAM использовано: {vram_used:.2f}GB")
        
        # Создаем изображение
        image = create_simple_document()
        
        # Простой тест OCR
        print(f"\n🔍 Тестируем OCR...")
        start_ocr = time.time()
        
        result = model.process_image(image, "Извлеки весь текст с изображения")
        ocr_time = time.time() - start_ocr
        
        print(f"✅ OCR завершен за {ocr_time:.2f}s")
        print(f"📝 Результат: {result}")
        
        # Проверяем качество
        keywords = ["ТЕСТ", "ИСПРАВЛЕНИЙ", "qwen3_vl_2b", "fp16", "ИСПРАВЛЕНО"]
        found = sum(1 for kw in keywords if kw.upper() in result.upper())
        quality = (found / len(keywords)) * 100
        
        print(f"🎯 Качество: {found}/{len(keywords)} ({quality:.0f}%)")
        
        # НЕ выгружаем модель
        print(f"🔄 Модель остается в памяти")
        
        if quality >= 60:
            print(f"🎉 ТЕСТ ПРОЙДЕН!")
            return True
        else:
            print(f"⚠️ Низкое качество OCR")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_model()
    exit(0 if success else 1)