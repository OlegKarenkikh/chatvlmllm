#!/usr/bin/env python3
"""
Финальный тест конфигурации - только совместимые модели
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import yaml

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_config():
    """Загружаем конфигурацию"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def create_test_image():
    """Создаем тестовое изображение"""
    img = Image.new('RGB', (300, 150), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), "ФИНАЛЬНЫЙ ТЕСТ", fill='black', font=font)
    draw.text((10, 40), "Модель: СОВМЕСТИМАЯ", fill='black', font=font)
    draw.text((10, 70), "Дата: 19.01.2026", fill='black', font=font)
    draw.text((10, 100), "Статус: ОК", fill='black', font=font)
    
    return img

def test_model_quick(model_name):
    """Быстрый тест модели"""
    print(f"\n🚀 ТЕСТ: {model_name}")
    print("-" * 30)
    
    try:
        from models.model_loader import ModelLoader
        
        # Загружаем
        start = time.time()
        model = ModelLoader.load_model(model_name)
        load_time = time.time() - start
        print(f"✅ Загружена: {load_time:.1f}s")
        
        # Обрабатываем
        image = create_test_image()
        start = time.time()
        result = model.process_image(image)
        process_time = time.time() - start
        print(f"✅ Обработка: {process_time:.1f}s")
        
        # Проверяем качество
        keywords = ["ФИНАЛЬНЫЙ", "ТЕСТ", "СОВМЕСТИМАЯ", "19.01.2026", "ОК"]
        found = sum(1 for kw in keywords if kw.upper() in result.upper())
        quality = (found / len(keywords)) * 100
        print(f"✅ Качество: {quality:.0f}% ({found}/{len(keywords)})")
        print(f"📝 Результат: {result[:50]}...")
        
        # Выгружаем
        model.unload()
        
        return {
            "success": True,
            "load_time": load_time,
            "process_time": process_time,
            "quality": quality
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Основная функция"""
    print("🔬 ФИНАЛЬНЫЙ ТЕСТ КОНФИГУРАЦИИ")
    print("=" * 50)
    
    # Проверяем GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ GPU: {gpu_name}")
        print(f"✅ VRAM: {vram_gb:.2f}GB")
    else:
        print("❌ GPU недоступна")
        return False
    
    # Загружаем конфигурацию
    config = load_config()
    available_models = list(config['models'].keys())
    
    print(f"📋 Доступные модели: {len(available_models)}")
    for model in available_models:
        model_info = config['models'][model]
        print(f"   - {model}: {model_info['name']}")
    
    # Тестируем все модели
    results = {}
    for model_name in available_models:
        result = test_model_quick(model_name)
        results[model_name] = result
        
        # Пауза между тестами
        time.sleep(1)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    # Сводка
    print("\n" + "=" * 50)
    print("📊 ФИНАЛЬНАЯ СВОДКА")
    print("=" * 50)
    
    working_models = 0
    for model_name, result in results.items():
        if result.get("success"):
            working_models += 1
            load_time = result.get("load_time", 0)
            process_time = result.get("process_time", 0)
            quality = result.get("quality", 0)
            print(f"✅ {model_name:15} | {load_time:5.1f}s | {process_time:5.1f}s | {quality:5.0f}%")
        else:
            error = result.get("error", "Unknown")
            print(f"❌ {model_name:15} | ОШИБКА: {error}")
    
    success_rate = (working_models / len(available_models)) * 100
    print(f"\n🏆 РЕЗУЛЬТАТ: {working_models}/{len(available_models)} моделей работают ({success_rate:.0f}%)")
    
    if working_models == len(available_models):
        print("🎉 ВСЕ МОДЕЛИ СОВМЕСТИМЫ И РАБОТАЮТ!")
        print("✅ СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ")
        return True
    else:
        print("⚠️ Есть проблемы с некоторыми моделями")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)