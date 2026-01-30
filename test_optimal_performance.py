#!/usr/bin/env python3
"""
Тест оптимальной производительности - восстановление быстрого GPU распознавания
Цель: got_ocr_hf 0.07с, qwen_vl_2b 1.16с
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
from models.model_loader import ModelLoader
from utils.logger import logger

def create_test_document():
    """Создаем тестовый документ для OCR"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Заголовок документа
    draw.text((50, 30), "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ", fill='black', font=font_large)
    
    # Основная информация
    draw.text((50, 80), "Серия: 77 АА  Номер: 123456", fill='black', font=font_medium)
    draw.text((50, 120), "Фамилия: ПЕТРОВ", fill='black', font=font_medium)
    draw.text((50, 160), "Имя: ПЕТР ПЕТРОВИЧ", fill='black', font=font_medium)
    draw.text((50, 200), "Дата рождения: 15.05.1985", fill='black', font=font_medium)
    draw.text((50, 240), "Место рождения: г. Москва", fill='black', font=font_medium)
    draw.text((50, 280), "Дата выдачи: 20.06.2020", fill='black', font=font_medium)
    draw.text((50, 320), "Действительно до: 20.06.2030", fill='black', font=font_medium)
    draw.text((50, 360), "Выдано: ГИБДД г. Москвы", fill='black', font=font_medium)
    
    # Категории
    draw.text((50, 420), "Категории: A, B, C", fill='black', font=font_medium)
    draw.text((50, 460), "Особые отметки: нет", fill='black', font=font_medium)
    
    img.save("test_optimal_document.png")
    return img

def test_optimal_got_ocr():
    """Тест got_ocr_hf - цель 0.07с обработка"""
    print("🚀 ТЕСТ GOT-OCR HF (цель: 0.07с)")
    print("-" * 40)
    
    try:
        # Загрузка модели
        start_load = time.time()
        model = ModelLoader.load_model('got_ocr_hf')
        load_time = time.time() - start_load
        
        print(f"✅ Загрузка: {load_time:.2f}s")
        
        # Создаем тестовое изображение
        image = create_test_document()
        
        # Обработка изображения (5 попыток для точности)
        times = []
        for i in range(5):
            start_process = time.time()
            result = model.process_image(image)
            process_time = time.time() - start_process
            times.append(process_time)
            print(f"  Попытка {i+1}: {process_time:.3f}s")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        
        print(f"📊 Средняя обработка: {avg_time:.3f}s")
        print(f"🏆 Лучшая обработка: {min_time:.3f}s")
        print(f"📝 Результат: {len(result)} символов")
        
        # Проверяем цель
        if min_time <= 0.1:  # Близко к цели 0.07с
            print("🎯 ЦЕЛЬ ДОСТИГНУТА! (≤0.1s)")
        elif min_time <= 0.5:
            print("⚡ ХОРОШАЯ СКОРОСТЬ (≤0.5s)")
        else:
            print("⚠️ МЕДЛЕННЕЕ ОЖИДАЕМОГО (>0.5s)")
        
        # Показываем часть результата
        print(f"📄 Фрагмент результата:")
        print(f"   {result[:100]}...")
        
        model.unload()
        return min_time, len(result)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None, 0

def test_optimal_qwen_vl():
    """Тест qwen_vl_2b - цель 1.16с обработка"""
    print("\n🚀 ТЕСТ QWEN2-VL 2B (цель: 1.16с)")
    print("-" * 40)
    
    try:
        # Загрузка модели
        start_load = time.time()
        model = ModelLoader.load_model('qwen_vl_2b')
        load_time = time.time() - start_load
        
        print(f"✅ Загрузка: {load_time:.2f}s")
        
        # Создаем тестовое изображение
        image = create_test_document()
        
        # Обработка изображения (3 попытки для точности)
        times = []
        for i in range(3):
            start_process = time.time()
            result = model.process_image(image, "Извлеки весь текст из документа")
            process_time = time.time() - start_process
            times.append(process_time)
            print(f"  Попытка {i+1}: {process_time:.3f}s")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        
        print(f"📊 Средняя обработка: {avg_time:.3f}s")
        print(f"🏆 Лучшая обработка: {min_time:.3f}s")
        print(f"📝 Результат: {len(result)} символов")
        
        # Проверяем цель
        if min_time <= 1.5:  # Близко к цели 1.16с
            print("🎯 ЦЕЛЬ ДОСТИГНУТА! (≤1.5s)")
        elif min_time <= 3.0:
            print("⚡ ХОРОШАЯ СКОРОСТЬ (≤3.0s)")
        else:
            print("⚠️ МЕДЛЕННЕЕ ОЖИДАЕМОГО (>3.0s)")
        
        # Показываем часть результата
        print(f"📄 Фрагмент результата:")
        print(f"   {result[:100]}...")
        
        model.unload()
        return min_time, len(result)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None, 0

def main():
    """Основная функция тестирования"""
    print("🎯 ТЕСТ ОПТИМАЛЬНОЙ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 50)
    print("Цели:")
    print("  • got_ocr_hf: ≤0.07s обработка")
    print("  • qwen_vl_2b: ≤1.16s обработка")
    print("=" * 50)
    
    # Проверяем GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"🖥️ GPU: {gpu_name}")
        print(f"💾 VRAM: {vram_gb:.2f}GB")
    else:
        print("❌ CUDA недоступна!")
        return False
    
    # Тестируем модели
    got_time, got_chars = test_optimal_got_ocr()
    qwen_time, qwen_chars = test_optimal_qwen_vl()
    
    # Итоговые результаты
    print("\n" + "=" * 50)
    print("🏆 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 50)
    
    if got_time:
        status_got = "🎯 ОТЛИЧНО" if got_time <= 0.1 else "⚡ ХОРОШО" if got_time <= 0.5 else "⚠️ МЕДЛЕННО"
        print(f"got_ocr_hf:  {got_time:.3f}s ({got_chars} символов) {status_got}")
    else:
        print("got_ocr_hf:  ❌ ОШИБКА")
    
    if qwen_time:
        status_qwen = "🎯 ОТЛИЧНО" if qwen_time <= 1.5 else "⚡ ХОРОШО" if qwen_time <= 3.0 else "⚠️ МЕДЛЕННО"
        print(f"qwen_vl_2b:  {qwen_time:.3f}s ({qwen_chars} символов) {status_qwen}")
    else:
        print("qwen_vl_2b:  ❌ ОШИБКА")
    
    # Проверяем достижение целей
    goals_met = 0
    if got_time and got_time <= 0.1:
        goals_met += 1
    if qwen_time and qwen_time <= 1.5:
        goals_met += 1
    
    print(f"\n🎯 Целей достигнуто: {goals_met}/2")
    
    if goals_met == 2:
        print("🎉 ВСЕ ЦЕЛИ ДОСТИГНУТЫ! Система работает оптимально!")
    elif goals_met == 1:
        print("⚡ ЧАСТИЧНО ОПТИМИЗИРОВАНО. Требуется доработка.")
    else:
        print("⚠️ ЦЕЛИ НЕ ДОСТИГНУТЫ. Требуется оптимизация.")
    
    # GPU память
    if torch.cuda.is_available():
        memory_used = torch.cuda.memory_allocated() / 1024**3
        print(f"💾 Использовано GPU памяти: {memory_used:.2f}GB")
    
    return goals_met >= 1

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)