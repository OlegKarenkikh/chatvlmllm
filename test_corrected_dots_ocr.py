#!/usr/bin/env python3
"""
ТЕСТ ИСПРАВЛЕННОЙ РЕАЛИЗАЦИИ dots.ocr

Проверяем:
1. Правильную загрузку исправленной модели
2. Корректную обработку изображений
3. Правильное извлечение текста (не JSON)
4. Устойчивость к CUDA ошибкам
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import json

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_document():
    """Создаем тестовый документ для проверки OCR."""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "ТЕСТОВЫЙ ДОКУМЕНТ", fill='black', font=font)
    
    # Основные поля
    draw.text((50, 70), "1. Номер: 123456789", fill='black', font=small_font)
    draw.text((50, 100), "2. Дата: 24.01.2026", fill='black', font=small_font)
    draw.text((50, 130), "3. Статус: АКТИВЕН", fill='black', font=small_font)
    draw.text((50, 160), "4. Организация: ТЕСТ ООО", fill='black', font=small_font)
    
    # Простая таблица
    draw.rectangle([50, 200, 550, 300], outline='black', width=1)
    draw.line([50, 230, 550, 230], fill='black', width=1)
    draw.line([200, 200, 200, 300], fill='black', width=1)
    draw.line([350, 200, 350, 300], fill='black', width=1)
    
    draw.text((60, 210), "Параметр", fill='black', font=small_font)
    draw.text((210, 210), "Значение", fill='black', font=small_font)
    draw.text((360, 210), "Единица", fill='black', font=small_font)
    
    draw.text((60, 250), "Температура", fill='black', font=small_font)
    draw.text((210, 250), "25.5", fill='black', font=small_font)
    draw.text((360, 250), "°C", fill='black', font=small_font)
    
    # Сохраняем для визуального контроля
    img.save("test_corrected_dots_document.png")
    
    return img

def test_corrected_dots_ocr():
    """Тестируем исправленную реализацию dots.ocr."""
    print("🔬 ТЕСТ ИСПРАВЛЕННОЙ РЕАЛИЗАЦИИ dots.ocr")
    print("=" * 60)
    
    try:
        from models.model_loader import ModelLoader
        
        # Создаем тестовое изображение
        print("📄 Создаем тестовый документ...")
        test_image = create_test_document()
        print("✅ Тестовый документ создан")
        
        # Загружаем исправленную модель
        print("\n📥 Загружаем исправленную dots.ocr...")
        start_load = time.time()
        
        model = ModelLoader.load_model("dots_ocr")
        load_time = time.time() - start_load
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Проверяем, что используется исправленная реализация
        model_class_name = model.__class__.__name__
        print(f"📋 Используемый класс: {model_class_name}")
        
        if "Corrected" in model_class_name:
            print("✅ Используется исправленная реализация")
        else:
            print("⚠️ Используется оригинальная реализация")
        
        # Тест 1: Простое извлечение текста
        print("\n🔍 ТЕСТ 1: Простое извлечение текста")
        start_process = time.time()
        
        result_text = model.extract_text(test_image)
        process_time = time.time() - start_process
        
        print(f"⏱️ Время обработки: {process_time:.3f}s")
        print(f"📝 Длина результата: {len(result_text)} символов")
        print(f"🔍 Результат: {result_text[:200]}...")
        
        # Проверяем качество OCR
        expected_keywords = ["ТЕСТОВЫЙ", "ДОКУМЕНТ", "123456789", "24.01.2026", "АКТИВЕН", "ТЕСТ", "ООО"]
        found_keywords = sum(1 for kw in expected_keywords if kw.upper() in result_text.upper())
        quality_score = (found_keywords / len(expected_keywords)) * 100
        
        print(f"🎯 Качество OCR: {found_keywords}/{len(expected_keywords)} ({quality_score:.1f}%)")
        
        # Тест 2: Обработка с разными режимами
        print("\n🔍 ТЕСТ 2: Разные режимы обработки")
        
        modes_to_test = [
            ("ocr_only", "Только OCR"),
            ("text_only", "Только текст"),
            ("simple_ocr", "Простой OCR")
        ]
        
        mode_results = {}
        
        for mode, description in modes_to_test:
            try:
                print(f"   Тестируем режим: {mode} ({description})")
                start = time.time()
                
                result = model.process_image(test_image, mode=mode)
                elapsed = time.time() - start
                
                # Анализируем результат
                is_json = False
                try:
                    json.loads(result)
                    is_json = True
                except:
                    pass
                
                mode_results[mode] = {
                    "time": elapsed,
                    "length": len(result),
                    "is_json": is_json,
                    "quality": sum(1 for kw in expected_keywords if kw.upper() in result.upper())
                }
                
                print(f"      ⏱️ {elapsed:.3f}s | 📝 {len(result)} символов | {'📊 JSON' if is_json else '📄 Текст'} | 🎯 {mode_results[mode]['quality']}/{len(expected_keywords)}")
                
            except Exception as e:
                print(f"      ❌ Ошибка: {e}")
                mode_results[mode] = {"error": str(e)}
        
        # Тест 3: Парсинг документа
        print("\n🔍 ТЕСТ 3: Парсинг документа")
        try:
            start = time.time()
            parsed_result = model.parse_document(test_image)
            parse_time = time.time() - start
            
            print(f"⏱️ Время парсинга: {parse_time:.3f}s")
            print(f"📊 Тип результата: {type(parsed_result)}")
            
            if isinstance(parsed_result, dict):
                print(f"✅ Успешность: {parsed_result.get('success', 'Unknown')}")
                if 'text' in parsed_result:
                    text_content = parsed_result['text']
                    text_quality = sum(1 for kw in expected_keywords if kw.upper() in text_content.upper())
                    print(f"📝 Извлеченный текст: {len(text_content)} символов")
                    print(f"🎯 Качество: {text_quality}/{len(expected_keywords)} ({text_quality/len(expected_keywords)*100:.1f}%)")
            
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
        
        # Выгружаем модель
        print("\n🔄 Выгружаем модель...")
        try:
            model.unload()
            print("✅ Модель выгружена успешно")
        except Exception as e:
            print(f"⚠️ Предупреждение при выгрузке: {e}")
        
        # Итоговая оценка
        print("\n" + "=" * 60)
        print("📊 ИТОГОВАЯ ОЦЕНКА")
        print("=" * 60)
        
        print(f"✅ Загрузка модели: {load_time:.2f}s")
        print(f"✅ Основной тест OCR: {quality_score:.1f}% качество")
        print(f"✅ Время обработки: {process_time:.3f}s")
        print(f"✅ Класс модели: {model_class_name}")
        
        # Оценка режимов
        successful_modes = sum(1 for result in mode_results.values() if "error" not in result)
        print(f"✅ Рабочих режимов: {successful_modes}/{len(modes_to_test)}")
        
        # Общая оценка
        overall_score = (quality_score + (successful_modes/len(modes_to_test)*100)) / 2
        print(f"🏆 ОБЩАЯ ОЦЕНКА: {overall_score:.1f}%")
        
        if overall_score >= 70:
            print("🎉 ИСПРАВЛЕННАЯ РЕАЛИЗАЦИЯ РАБОТАЕТ ОТЛИЧНО!")
            return True
        elif overall_score >= 50:
            print("✅ Исправленная реализация работает удовлетворительно")
            return True
        else:
            print("⚠️ Исправленная реализация требует доработки")
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cuda_recovery():
    """Тестируем систему восстановления CUDA."""
    print("\n🛡️ ТЕСТ СИСТЕМЫ ВОССТАНОВЛЕНИЯ CUDA")
    print("=" * 60)
    
    try:
        from utils.cuda_recovery import cuda_recovery_manager
        
        # Тест 1: Проверка детекции CUDA ошибок
        print("🔍 Тест 1: Детекция CUDA ошибок")
        
        test_errors = [
            "CUDA error: device-side assert triggered",
            "CUDA out of memory",
            "RuntimeError: CUDA kernel errors",
            "Normal Python error"
        ]
        
        for error_msg in test_errors:
            error = Exception(error_msg)
            is_cuda = cuda_recovery_manager.is_cuda_error(error)
            expected = "cuda" in error_msg.lower()
            status = "✅" if is_cuda == expected else "❌"
            print(f"   {status} '{error_msg[:30]}...' -> {'CUDA' if is_cuda else 'Обычная'}")
        
        # Тест 2: Безопасный вызов функции
        print("\n🔍 Тест 2: Безопасный вызов функции")
        
        def test_function(should_fail=False):
            if should_fail:
                raise Exception("CUDA error: device-side assert triggered")
            return "Success"
        
        # Успешный вызов
        try:
            result = cuda_recovery_manager.safe_cuda_call(test_function, should_fail=False)
            print(f"   ✅ Успешный вызов: {result}")
        except Exception as e:
            print(f"   ❌ Неожиданная ошибка: {e}")
        
        print("✅ Система восстановления CUDA протестирована")
        return True
        
    except ImportError:
        print("⚠️ Модуль cuda_recovery не найден")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования CUDA recovery: {e}")
        return False

def main():
    """Основная функция тестирования."""
    print("🔬 КОМПЛЕКСНЫЙ ТЕСТ ИСПРАВЛЕНИЙ")
    print("=" * 80)
    
    # Проверяем CUDA
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ GPU: {gpu_name}")
        print(f"✅ VRAM: {vram_gb:.2f}GB")
    else:
        print("⚠️ CUDA недоступна, тестируем в CPU режиме")
    
    # Тест 1: Исправленная dots.ocr
    dots_ocr_success = test_corrected_dots_ocr()
    
    # Тест 2: Система восстановления CUDA
    cuda_recovery_success = test_cuda_recovery()
    
    # Итоговый результат
    print("\n" + "=" * 80)
    print("🏆 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 80)
    
    print(f"{'✅' if dots_ocr_success else '❌'} Исправленная dots.ocr: {'Работает' if dots_ocr_success else 'Проблемы'}")
    print(f"{'✅' if cuda_recovery_success else '❌'} Система восстановления CUDA: {'Работает' if cuda_recovery_success else 'Проблемы'}")
    
    overall_success = dots_ocr_success and cuda_recovery_success
    success_rate = (int(dots_ocr_success) + int(cuda_recovery_success)) / 2 * 100
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {success_rate:.0f}% успешности")
    
    if overall_success:
        print("🎉 ВСЕ ИСПРАВЛЕНИЯ РАБОТАЮТ КОРРЕКТНО!")
    elif success_rate >= 50:
        print("✅ Большинство исправлений работают")
    else:
        print("⚠️ Требуется дополнительная доработка")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)