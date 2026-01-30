#!/usr/bin/env python3
"""
Тест интеграции dots.ocr с chatvlmllm проектом
"""

import sys
import os
import torch
from PIL import Image, ImageDraw, ImageFont
import json
import time

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.dots_ocr_chatvlm_integration import DotsOCRChatVLM, initialize_dots_ocr, get_dots_ocr_instance

def create_test_image():
    """Создание тестового изображения с текстом"""
    # Создаем изображение
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Добавляем текст
    try:
        # Пытаемся использовать системный шрифт
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback на стандартный шрифт
        font = ImageFont.load_default()
    
    # Текст на разных языках
    texts = [
        "ТЕСТОВЫЙ ДОКУМЕНТ",
        "Test Document in English", 
        "Номер документа: 123456789",
        "Document Number: 123456789",
        "Дата: 24 января 2026",
        "Date: January 24, 2026"
    ]
    
    y_position = 50
    for text in texts:
        draw.text((50, y_position), text, fill='black', font=font)
        y_position += 40
    
    # Добавляем рамку
    draw.rectangle([30, 30, 770, 570], outline='black', width=2)
    
    # Сохраняем
    img.save('test_chatvlm_document.png')
    return 'test_chatvlm_document.png'

def test_openai_format():
    """Тест в формате OpenAI API (как в chatvlmllm)"""
    print("🧪 ТЕСТ OPENAI API ФОРМАТА")
    print("-" * 40)
    
    # Создаем тестовое изображение
    image_path = create_test_image()
    print(f"📄 Создано тестовое изображение: {image_path}")
    
    # Получаем экземпляр модели
    dots_ocr = get_dots_ocr_instance()
    
    # Тестовые сообщения в формате OpenAI
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": image_path}
                },
                {
                    "type": "text",
                    "text": "Extract all text from this document. Provide both Russian and English text."
                }
            ]
        }
    ]
    
    print("🔍 Обрабатываем через dots.ocr...")
    start_time = time.time()
    
    result = dots_ocr.chat_completion(messages, max_tokens=1024)
    
    processing_time = time.time() - start_time
    
    print(f"⏱️ Время обработки: {processing_time:.3f}s")
    print()
    
    # Анализ результата
    if 'error' in result:
        print(f"❌ Ошибка: {result['error']}")
        return False
    else:
        print("✅ Успешная обработка!")
        content = result['choices'][0]['message']['content']
        print(f"📝 Извлеченный текст ({len(content)} символов):")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        # Проверяем качество распознавания
        expected_words = ['ТЕСТОВЫЙ', 'ДОКУМЕНТ', 'Test', 'Document', '123456789', '2026']
        found_words = sum(1 for word in expected_words if word in content)
        
        print(f"🎯 Качество распознавания: {found_words}/{len(expected_words)} слов найдено")
        
        if found_words >= len(expected_words) // 2:
            print("✅ Качество распознавания приемлемое")
            return True
        else:
            print("⚠️ Низкое качество распознавания")
            return False

def test_different_formats():
    """Тест различных форматов входных данных"""
    print("\n🧪 ТЕСТ РАЗЛИЧНЫХ ФОРМАТОВ")
    print("-" * 40)
    
    dots_ocr = get_dots_ocr_instance()
    image_path = 'test_chatvlm_document.png'
    
    # Формат 1: Простой текст
    messages1 = [
        {
            "role": "user",
            "content": "Extract text from image"
        }
    ]
    
    # Формат 2: Только изображение
    messages2 = [
        {
            "role": "user", 
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": image_path}
                }
            ]
        }
    ]
    
    # Формат 3: Полный формат
    messages3 = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": image_path}
                },
                {
                    "type": "text",
                    "text": "Please extract all visible text"
                }
            ]
        }
    ]
    
    formats = [
        ("Простой текст", messages1),
        ("Только изображение", messages2), 
        ("Полный формат", messages3)
    ]
    
    results = []
    
    for format_name, messages in formats:
        print(f"🔍 Тестируем формат: {format_name}")
        
        result = dots_ocr.chat_completion(messages)
        
        if 'error' in result:
            print(f"❌ Ошибка: {result['error']}")
            results.append(False)
        else:
            content = result['choices'][0]['message']['content']
            print(f"✅ Успех: {len(content)} символов")
            results.append(True)
        
        print()
    
    success_rate = sum(results) / len(results) * 100
    print(f"📊 Успешность форматов: {success_rate:.1f}%")
    
    return success_rate >= 66.7  # Минимум 2 из 3 форматов должны работать

def test_performance():
    """Тест производительности"""
    print("\n🧪 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("-" * 40)
    
    dots_ocr = get_dots_ocr_instance()
    image_path = 'test_chatvlm_document.png'
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url", 
                    "image_url": {"url": image_path}
                },
                {
                    "type": "text",
                    "text": "Extract text quickly"
                }
            ]
        }
    ]
    
    # Несколько прогонов для измерения производительности
    times = []
    
    for i in range(3):
        print(f"🔄 Прогон {i+1}/3...")
        
        start_time = time.time()
        result = dots_ocr.chat_completion(messages)
        end_time = time.time()
        
        if 'error' not in result:
            processing_time = end_time - start_time
            times.append(processing_time)
            print(f"⏱️ Время: {processing_time:.3f}s")
        else:
            print(f"❌ Ошибка в прогоне {i+1}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 СТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ:")
        print(f"⚡ Среднее время: {avg_time:.3f}s")
        print(f"🏃 Минимальное время: {min_time:.3f}s") 
        print(f"🐌 Максимальное время: {max_time:.3f}s")
        
        # Оценка производительности
        if avg_time < 60:
            print("✅ Отличная производительность")
            return True
        elif avg_time < 120:
            print("⚠️ Приемлемая производительность")
            return True
        else:
            print("❌ Низкая производительность")
            return False
    else:
        print("❌ Не удалось измерить производительность")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТ ИНТЕГРАЦИИ DOTS.OCR С CHATVLMLLM")
    print("=" * 60)
    
    # Информация о системе
    print(f"🖥️ GPU: {torch.cuda.get_device_name(0)}")
    print(f"🔧 Compute Capability: {torch.cuda.get_device_capability(0)}")
    print(f"🐍 PyTorch: {torch.__version__}")
    print(f"⚡ CUDA: {torch.version.cuda}")
    print(f"💾 VRAM доступно: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    print()
    
    # Инициализация модели
    print("🔄 Инициализация dots.ocr...")
    if not initialize_dots_ocr():
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить dots.ocr")
        print("💡 Проверьте:")
        print("   - Установлены ли все зависимости")
        print("   - Доступна ли модель rednote-hilab/dots.ocr")
        print("   - Достаточно ли VRAM (требуется ~19GB)")
        return False
    
    print("✅ dots.ocr успешно загружена")
    print()
    
    # Запуск тестов
    tests = [
        ("OpenAI API формат", test_openai_format),
        ("Различные форматы", test_different_formats),
        ("Производительность", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Запуск теста: {test_name}")
        try:
            result = test_func()
            results.append(result)
            print(f"{'✅ ПРОЙДЕН' if result else '❌ НЕ ПРОЙДЕН'}")
        except Exception as e:
            print(f"❌ ОШИБКА В ТЕСТЕ: {e}")
            results.append(False)
        
        print()
    
    # Итоговый отчет
    passed_tests = sum(results)
    total_tests = len(results)
    success_rate = passed_tests / total_tests * 100
    
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    print(f"✅ Пройдено тестов: {passed_tests}/{total_tests}")
    print(f"📈 Успешность: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 ОТЛИЧНО! dots.ocr готова для использования в chatvlmllm")
        status = "ГОТОВА К ПРОДАКШЕНУ"
    elif success_rate >= 60:
        print("⚠️ ХОРОШО! dots.ocr работает, но есть проблемы")
        status = "ТРЕБУЕТ ДОРАБОТКИ"
    else:
        print("❌ ПЛОХО! dots.ocr имеет серьезные проблемы")
        status = "НЕ ГОТОВА"
    
    # Сохранение результатов
    test_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "gpu": torch.cuda.get_device_name(0),
        "pytorch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "tests_passed": passed_tests,
        "total_tests": total_tests,
        "success_rate": success_rate,
        "status": status,
        "individual_results": dict(zip([t[0] for t in tests], results))
    }
    
    with open('dots_ocr_chatvlm_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: dots_ocr_chatvlm_test_results.json")
    print(f"🏷️ Статус интеграции: {status}")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 ИНТЕГРАЦИЯ УСПЕШНА! Можно использовать dots.ocr в chatvlmllm")
    else:
        print("\n❌ ИНТЕГРАЦИЯ НЕУСПЕШНА! Требуется дополнительная настройка")
    
    # Очистка
    try:
        dots_ocr = get_dots_ocr_instance()
        dots_ocr.cleanup()
    except:
        pass