#!/usr/bin/env python3
"""
Тест исправленной got_ocr_hf модели с защитой от зависания
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import threading

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TimeoutError(Exception):
    pass

def run_with_timeout(func, timeout_seconds):
    """Запускает функцию с таймаутом (Windows-совместимо)"""
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        raise TimeoutError(f"Операция превысила лимит времени ({timeout_seconds}s)")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]

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
    draw.text((20, 140), "Температура: 25.5°C", fill='black', font=font)
    
    return img

def test_got_ocr_fixed():
    """Тест исправленной got_ocr_hf с таймаутом"""
    print("🚀 ТЕСТ ИСПРАВЛЕННОЙ GOT-OCR HF")
    print("=" * 45)
    
    # Проверяем GPU
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        print(f"✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f}GB")
    else:
        print("❌ GPU недоступна")
        return False
    
    try:
        from models.model_loader import ModelLoader
        
        print("📥 Загружаем got_ocr_hf...")
        start_time = time.time()
        
        # Загружаем модель с таймаутом (Windows-совместимо)
        def load_model():
            from models.model_loader import ModelLoader
            return ModelLoader.load_model('got_ocr_hf')
        
        try:
            model = run_with_timeout(load_model, 60)
        except TimeoutError:
            print("❌ ТАЙМАУТ: Загрузка модели превысила 60 секунд")
            return False
        
        load_time = time.time() - start_time
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Создаем документ для OCR
        print("🖼️ Создаем тестовый документ...")
        image = create_simple_document()
        
        # OCR обработка с таймаутом
        print("🔍 Выполняем OCR (таймаут 30s)...")
        start_process = time.time()
        
        # Обрабатываем с таймаутом (Windows-совместимо)
        def process_image():
            return model.process_image(image)
        
        try:
            result = run_with_timeout(process_image, 30)
        except TimeoutError:
            print("❌ ТАЙМАУТ: Обработка превысила 30 секунд")
            model.unload()
            return False
        
        process_time = time.time() - start_process
        
        print(f"✅ OCR завершен за {process_time:.3f}s")
        print(f"📝 Результат ({len(result)} символов):")
        print(f"   {result}")
        
        # Проверяем качество OCR
        keywords = ["ТЕСТОВЫЙ", "ДОКУМЕНТ", "123456789", "19.01.2026", "АКТИВЕН", "25.5"]
        found = sum(1 for kw in keywords if kw.upper() in result.upper())
        quality = (found / len(keywords)) * 100
        
        print(f"🎯 Качество OCR: {found}/{len(keywords)} ключевых слов ({quality:.1f}%)")
        
        # Проверяем на мусорный вывод
        garbage_indicators = ["Champion", "kaps", "ADDR", "ĠĠĠ", "ĊĊĊ"]
        is_garbage = any(indicator in result for indicator in garbage_indicators)
        
        if is_garbage:
            print("⚠️ ОБНАРУЖЕН МУСОРНЫЙ ВЫВОД!")
            status = "МУСОР"
        elif quality >= 80:
            print("🏆 ОТЛИЧНОЕ КАЧЕСТВО OCR!")
            status = "ОТЛИЧНО"
        elif quality >= 60:
            print("👍 ХОРОШЕЕ КАЧЕСТВО OCR!")
            status = "ХОРОШО"
        elif quality >= 30:
            print("⚠️ СРЕДНЕЕ КАЧЕСТВО OCR")
            status = "СРЕДНЕ"
        else:
            print("❌ НИЗКОЕ КАЧЕСТВО OCR")
            status = "ПЛОХО"
        
        # Выгружаем модель
        print("🔄 Выгружаем модель...")
        model.unload()
        
        print(f"🎉 ТЕСТ ЗАВЕРШЕН: {status}")
        print(f"⚡ Производительность: загрузка {load_time:.2f}s, обработка {process_time:.3f}s")
        
        return status in ["ОТЛИЧНО", "ХОРОШО"]
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_got_ocr_fixed()
    print(f"\n{'✅ УСПЕХ' if success else '❌ НЕУДАЧА'}")
    exit(0 if success else 1)