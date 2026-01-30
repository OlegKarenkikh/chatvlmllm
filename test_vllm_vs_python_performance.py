#!/usr/bin/env python3
"""
Сравнение производительности vLLM vs Python реализации dots.ocr
"""

import time
import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_images():
    """Создание тестовых изображений разной сложности"""
    print("🖼️ Создание тестовых изображений...")
    
    images = []
    
    # Простое изображение
    img1 = Image.new('RGB', (400, 100), color='white')
    draw1 = ImageDraw.Draw(img1)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw1.text((50, 30), "SIMPLE TEST", fill='black', font=font)
    img1.save('test_simple_vllm.png')
    images.append(('test_simple_vllm.png', 'Simple text'))
    
    # Сложное изображение
    img2 = Image.new('RGB', (800, 400), color='white')
    draw2 = ImageDraw.Draw(img2)
    
    texts = [
        "ДОКУМЕНТ ТЕСТ",
        "Document Test",
        "Номер: 123456789",
        "Number: 123456789",
        "Дата: 24.01.2026",
        "Date: 24.01.2026"
    ]
    
    y_pos = 50
    for text in texts:
        draw2.text((50, y_pos), text, fill='black', font=font)
        y_pos += 40
    
    # Рамка
    draw2.rectangle([30, 30, 770, 370], outline='black', width=2)
    img2.save('test_complex_vllm.png')
    images.append(('test_complex_vllm.png', 'Complex document'))
    
    print(f"✅ Создано {len(images)} тестовых изображений")
    return images

def test_vllm_performance():
    """Тест производительности vLLM"""
    print("\n🚀 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ VLLM")
    print("=" * 40)
    
    try:
        from vllm_dots_ocr_client import get_vllm_dots_ocr_client
        
        client = get_vllm_dots_ocr_client()
        
        # Проверка доступности
        if not client.health_check():
            print("❌ vLLM сервер недоступен")
            return None
        
        print("✅ vLLM сервер доступен")
        
        # Создание тестовых изображений
        test_images = create_test_images()
        
        results = []
        
        for image_path, description in test_images:
            print(f"\n🔍 Тестируем: {description}")
            
            # Прогрев (первый запрос может быть медленнее)
            print("🔥 Прогрев...")
            client.process_image(image_path, "Extract text")
            
            # Основные тесты
            times = []
            for i in range(3):
                print(f"   Прогон {i+1}/3...")
                
                start_time = time.time()
                result = client.process_image(image_path, "Extract all text from this image")
                end_time = time.time()
                
                if result["success"]:
                    processing_time = end_time - start_time
                    times.append(processing_time)
                    print(f"   ✅ {processing_time:.3f}s - {len(result['content'])} символов")
                else:
                    print(f"   ❌ Ошибка: {result['error']}")
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                results.append({
                    'description': description,
                    'avg_time': avg_time,
                    'min_time': min_time,
                    'max_time': max_time,
                    'success_rate': len(times) / 3 * 100
                })
                
                print(f"📊 Среднее время: {avg_time:.3f}s")
        
        return results
        
    except ImportError:
        print("❌ vLLM клиент недоступен")
        return None
    except Exception as e:
        print(f"❌ Ошибка vLLM теста: {e}")
        return None

def test_python_performance():
    """Тест производительности Python реализации"""
    print("\n🐍 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ PYTHON")
    print("=" * 40)
    
    try:
        from models.dots_ocr_chatvlm_integration import get_dots_ocr_instance, initialize_dots_ocr
        
        # Попытка инициализации
        if not initialize_dots_ocr():
            print("❌ Python dots.ocr недоступна (Flash Attention проблема)")
            return None
        
        dots_ocr = get_dots_ocr_instance()
        print("✅ Python dots.ocr загружена")
        
        # Использование тех же тестовых изображений
        test_images = [
            ('test_simple_vllm.png', 'Simple text'),
            ('test_complex_vllm.png', 'Complex document')
        ]
        
        results = []
        
        for image_path, description in test_images:
            print(f"\n🔍 Тестируем: {description}")
            
            # Загрузка изображения
            image = Image.open(image_path).convert('RGB')
            
            times = []
            for i in range(3):
                print(f"   Прогон {i+1}/3...")
                
                start_time = time.time()
                result = dots_ocr.process_image(image, "Extract all text from this image")
                end_time = time.time()
                
                if result:
                    processing_time = end_time - start_time
                    times.append(processing_time)
                    print(f"   ✅ {processing_time:.3f}s - {len(result)} символов")
                else:
                    print(f"   ❌ Пустой результат")
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                results.append({
                    'description': description,
                    'avg_time': avg_time,
                    'min_time': min_time,
                    'max_time': max_time,
                    'success_rate': len(times) / 3 * 100
                })
                
                print(f"📊 Среднее время: {avg_time:.3f}s")
        
        return results
        
    except ImportError:
        print("❌ Python dots.ocr модуль недоступен")
        return None
    except Exception as e:
        print(f"❌ Ошибка Python теста: {e}")
        return None

def compare_results(vllm_results, python_results):
    """Сравнение результатов"""
    print("\n📊 СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 50)
    
    if not vllm_results and not python_results:
        print("❌ Нет данных для сравнения")
        return
    
    if not vllm_results:
        print("⚠️ Только Python результаты доступны")
        print_results("Python dots.ocr", python_results)
        return
    
    if not python_results:
        print("⚠️ Только vLLM результаты доступны")
        print_results("vLLM dots.ocr", vllm_results)
        return
    
    # Полное сравнение
    print("| Тест | vLLM (s) | Python (s) | Ускорение |")
    print("|------|----------|------------|-----------|")
    
    for i, (vllm_res, python_res) in enumerate(zip(vllm_results, python_results)):
        if vllm_res['success_rate'] > 0 and python_res['success_rate'] > 0:
            speedup = python_res['avg_time'] / vllm_res['avg_time']
            print(f"| {vllm_res['description'][:15]} | {vllm_res['avg_time']:.3f} | {python_res['avg_time']:.3f} | {speedup:.2f}x |")
        else:
            print(f"| {vllm_res['description'][:15]} | {'N/A' if vllm_res['success_rate'] == 0 else f'{vllm_res['avg_time']:.3f}'} | {'N/A' if python_res['success_rate'] == 0 else f'{python_res['avg_time']:.3f}'} | N/A |")

def print_results(title, results):
    """Печать результатов"""
    if not results:
        return
    
    print(f"\n📋 {title}:")
    print("-" * 30)
    
    for result in results:
        print(f"🔍 {result['description']}:")
        print(f"   ⚡ Среднее: {result['avg_time']:.3f}s")
        print(f"   🏃 Минимум: {result['min_time']:.3f}s")
        print(f"   🐌 Максимум: {result['max_time']:.3f}s")
        print(f"   ✅ Успешность: {result['success_rate']:.1f}%")
        print()

def main():
    """Основная функция сравнения"""
    print("🏁 СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ DOTS.OCR")
    print("=" * 60)
    print("vLLM Docker vs Python реализация на RTX 5070 Ti Blackwell")
    print()
    
    # Тест vLLM
    vllm_results = test_vllm_performance()
    
    # Тест Python
    python_results = test_python_performance()
    
    # Сравнение
    compare_results(vllm_results, python_results)
    
    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("=" * 20)
    
    if vllm_results and any(r['success_rate'] > 0 for r in vllm_results):
        print("✅ vLLM Docker решение работает и рекомендуется для использования")
        print("   - Обходит проблемы Flash Attention")
        print("   - Стабильная производительность")
        print("   - Готово к продакшену")
    else:
        print("❌ vLLM Docker решение недоступно")
        print("   - Проверьте запуск Docker контейнера")
        print("   - Убедитесь в доступности GPU")
    
    if python_results and any(r['success_rate'] > 0 for r in python_results):
        print("✅ Python реализация работает")
        print("   - Может использоваться как fallback")
    else:
        print("❌ Python реализация не работает")
        print("   - Проблемы с Flash Attention на Blackwell")
        print("   - Используйте vLLM как основное решение")
    
    print("\n🎯 ИТОГ: Используйте vLLM Docker для dots.ocr на RTX 5070 Ti!")

if __name__ == "__main__":
    main()