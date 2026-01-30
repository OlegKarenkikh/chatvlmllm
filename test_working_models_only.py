#!/usr/bin/env python3
"""
Тест только рабочих моделей (без got_ocr_hf)
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_document():
    """Создаем тестовый документ для OCR"""
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

def test_model(model_name):
    """Тестирует одну модель"""
    print(f"\n🚀 ТЕСТ: {model_name}")
    print("-" * 40)
    
    try:
        from models.model_loader import ModelLoader
        
        # Загружаем модель
        print("📥 Загружаем модель...")
        start_load = time.time()
        
        model = ModelLoader.load_model(model_name)
        load_time = time.time() - start_load
        
        print(f"✅ Загружена за {load_time:.2f}s")
        
        # Создаем изображение
        image = create_test_document()
        
        # Обрабатываем
        print("🔍 Обрабатываем...")
        start_process = time.time()
        
        result = model.process_image(image)
        process_time = time.time() - start_process
        
        print(f"✅ Обработано за {process_time:.3f}s")
        print(f"📝 Результат ({len(result)} символов): {result[:100]}...")
        
        # Проверяем качество
        keywords = ["ТЕСТОВЫЙ", "ДОКУМЕНТ", "123456789", "19.01.2026", "АКТИВЕН"]
        found = sum(1 for kw in keywords if kw.upper() in result.upper())
        quality = (found / len(keywords)) * 100
        
        print(f"🎯 Качество: {found}/{len(keywords)} ({quality:.1f}%)")
        
        # Выгружаем
        model.unload()
        
        return {
            "status": "success",
            "load_time": load_time,
            "process_time": process_time,
            "quality": quality,
            "output_length": len(result)
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {"status": "error", "error": str(e)}

def main():
    """Основная функция"""
    print("🔬 ТЕСТ РАБОЧИХ МОДЕЛЕЙ")
    print("=" * 50)
    
    # Только рабочие модели (без got_ocr_hf)
    working_models = [
        "qwen_vl_2b",      # Основная OCR
        "qwen3_vl_2b",     # Многоязычная
        "dots_ocr",        # Парсер документов
    ]
    
    results = {}
    
    for model_name in working_models:
        try:
            result = test_model(model_name)
            results[model_name] = result
            
            # Пауза для очистки памяти
            time.sleep(1)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            results[model_name] = {"status": "critical_error", "error": str(e)}
    
    # Сводка
    print("\n" + "=" * 50)
    print("📊 СВОДКА РЕЗУЛЬТАТОВ")
    print("=" * 50)
    
    working_count = 0
    for model_name, result in results.items():
        if result.get("status") == "success":
            working_count += 1
            load_time = result.get("load_time", 0)
            process_time = result.get("process_time", 0)
            quality = result.get("quality", 0)
            print(f"✅ {model_name:15} | {load_time:6.2f}s | {process_time:6.3f}s | {quality:5.1f}%")
        else:
            error = result.get("error", "Unknown")
            print(f"❌ {model_name:15} | ОШИБКА: {error}")
    
    print(f"\n🏆 ИТОГ: {working_count}/{len(working_models)} моделей работают ({working_count/len(working_models)*100:.1f}%)")
    
    if working_count == len(working_models):
        print("🎉 ВСЕ РАБОЧИЕ МОДЕЛИ ФУНКЦИОНИРУЮТ КОРРЕКТНО!")
        return True
    else:
        print("⚠️ Есть проблемы с некоторыми моделями")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)