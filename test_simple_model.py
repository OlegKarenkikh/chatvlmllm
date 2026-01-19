#!/usr/bin/env python3
"""
Простой тест одной модели без зависания
"""

import time
import torch
from PIL import Image
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_qwen():
    """Простой тест qwen_vl_2b"""
    print("🚀 ПРОСТОЙ ТЕСТ QWEN2-VL 2B")
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
        
        print("📥 Загружаем модель...")
        start_time = time.time()
        
        # Загружаем модель с таймаутом
        model = ModelLoader.load_model('qwen_vl_2b')
        load_time = time.time() - start_time
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Создаем простое изображение
        print("🖼️ Создаем тестовое изображение...")
        image = Image.new('RGB', (200, 100), color='white')
        
        # Простая обработка
        print("🔍 Обрабатываем изображение...")
        start_process = time.time()
        
        result = model.process_image(image, "Что на изображении?")
        process_time = time.time() - start_process
        
        print(f"✅ Обработка завершена за {process_time:.2f}s")
        print(f"📝 Результат: {result}")
        
        # Выгружаем модель
        print("🔄 Выгружаем модель...")
        model.unload()
        
        print("🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_qwen()
    exit(0 if success else 1)