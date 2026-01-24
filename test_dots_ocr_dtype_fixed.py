#!/usr/bin/env python3
"""
ТЕСТ DTYPE-ИСПРАВЛЕННОЙ DOTS.OCR

Проверяем исправление проблемы:
Input type (struct c10::BFloat16) and bias type (struct c10::Half) should be the same
"""

import time
import torch
import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_document():
    """Создаем тестовый документ для проверки OCR."""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 18)
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        font = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "DTYPE FIX TEST DOCUMENT", fill='black', font=title_font)
    
    # Основная информация
    draw.text((50, 80), "Document ID: DTYPE-FIX-2026", fill='black', font=font)
    draw.text((50, 110), "Date: January 24, 2026", fill='black', font=font)
    draw.text((50, 140), "Status: TESTING", fill='black', font=font)
    draw.text((50, 170), "Purpose: Fix BFloat16/Half mismatch", fill='black', font=font)
    
    # Дополнительный текст
    draw.text((50, 220), "Expected Results:", fill='black', font=font)
    draw.text((50, 250), "• No dtype errors", fill='black', font=font)
    draw.text((50, 280), "• Successful text extraction", fill='black', font=font)
    draw.text((50, 310), "• Fast processing time", fill='black', font=font)
    
    # Сохраняем для визуального контроля
    img.save("test_dtype_fix_document.png")
    
    return img

def test_dtype_fixed_dots_ocr():
    """Тестируем dtype-исправленную dots.ocr."""
    print("🔧 ТЕСТ DTYPE-ИСПРАВЛЕННОЙ DOTS.OCR")
    print("=" * 50)
    
    try:
        from models.model_loader import ModelLoader
        
        # Создаем тестовое изображение
        test_image = create_test_document()
        
        # Загружаем dtype-исправленную модель
        print("📥 Загружаем dtype-исправленную dots.ocr...")
        start_load = time.time()
        
        model = ModelLoader.load_model("dots_ocr")  # Теперь автоматически использует dtype-fixed версию
        load_time = time.time() - start_load
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        print(f"📋 Класс модели: {model.__class__.__name__}")
        
        # Тест 1: Простое извлечение текста
        print("\n🔍 Тест 1: Простое извлечение текста")
        start_process = time.time()
        
        try:
            result = model.extract_text(test_image)
            process_time = time.time() - start_process
            
            print(f"⏱️ Время обработки: {process_time:.3f}s")
            print(f"📝 Длина результата: {len(result)} символов")
            print(f"🔍 Результат: {result[:200]}...")
            
            # Проверяем на ошибки dtype
            if "BFloat16" in result or "Half" in result:
                print("❌ Dtype ошибка все еще присутствует!")
                dtype_error = True
            else:
                print("✅ Dtype ошибка исправлена!")
                dtype_error = False
            
            # Анализируем качество
            expected_keywords = ["DTYPE", "FIX", "TEST", "DOCUMENT", "DTYPE-FIX-2026", "TESTING"]
            found_keywords = sum(1 for kw in expected_keywords if kw.upper() in result.upper())
            quality_score = (found_keywords / len(expected_keywords)) * 100
            
            print(f"🎯 Качество OCR: {found_keywords}/{len(expected_keywords)} ({quality_score:.1f}%)")
            
            test1_success = not dtype_error and quality_score > 0
            
        except Exception as e:
            print(f"❌ Ошибка в тесте 1: {e}")
            test1_success = False
            dtype_error = "BFloat16" in str(e) or "Half" in str(e)
            quality_score = 0
            process_time = 0
        
        # Тест 2: Чат с моделью
        print("\n🔍 Тест 2: Чат с моделью")
        start_chat = time.time()
        
        try:
            chat_result = model.chat(test_image, "What is the document ID?")
            chat_time = time.time() - start_chat
            
            print(f"⏱️ Время чата: {chat_time:.3f}s")
            print(f"💬 Ответ чата: {chat_result[:100]}...")
            
            # Проверяем, содержит ли ответ ID документа
            chat_success = "DTYPE-FIX-2026" in chat_result.upper()
            print(f"🎯 Чат успешен: {'✅' if chat_success else '❌'}")
            
        except Exception as e:
            print(f"❌ Ошибка в тесте 2: {e}")
            chat_success = False
            chat_time = 0
        
        # Тест 3: Парсинг документа
        print("\n🔍 Тест 3: Парсинг документа")
        start_parse = time.time()
        
        try:
            parsed_result = model.parse_document(test_image)
            parse_time = time.time() - start_parse
            
            print(f"⏱️ Время парсинга: {parse_time:.3f}s")
            print(f"✅ Успешность парсинга: {parsed_result.get('success', False)}")
            print(f"📄 Метод: {parsed_result.get('method', 'unknown')}")
            
            parse_success = parsed_result.get('success', False)
            
        except Exception as e:
            print(f"❌ Ошибка в тесте 3: {e}")
            parse_success = False
            parse_time = 0
        
        # Выгружаем модель
        model.unload()
        
        # Итоговый анализ
        print("\n" + "=" * 50)
        print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ DTYPE FIX")
        print("=" * 50)
        
        print(f"✅ Загрузка модели: {load_time:.2f}s")
        print(f"{'✅' if test1_success else '❌'} Извлечение текста: {quality_score:.1f}% качество")
        print(f"{'✅' if not dtype_error else '❌'} Dtype ошибка: {'Исправлена' if not dtype_error else 'Присутствует'}")
        print(f"{'✅' if chat_success else '❌'} Чат функция: {'Работает' if chat_success else 'Не работает'}")
        print(f"{'✅' if parse_success else '❌'} Парсинг документа: {'Работает' if parse_success else 'Не работает'}")
        
        # Общая оценка
        total_tests = 4  # загрузка, извлечение, чат, парсинг
        passed_tests = sum([
            True,  # загрузка всегда успешна если дошли до сюда
            test1_success,
            chat_success,
            parse_success
        ])
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {passed_tests}/{total_tests} тестов пройдено ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("🎉 DTYPE FIX РАБОТАЕТ ОТЛИЧНО!")
            final_status = "excellent"
        elif success_rate >= 50:
            print("✅ Dtype fix работает удовлетворительно")
            final_status = "good"
        else:
            print("⚠️ Требуется дополнительная доработка")
            final_status = "needs_work"
        
        # Сохраняем результаты
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_class": model.__class__.__name__,
            "load_time": load_time,
            "dtype_error_fixed": not dtype_error,
            "text_extraction": {
                "success": test1_success,
                "quality_score": quality_score,
                "process_time": process_time
            },
            "chat_function": {
                "success": chat_success,
                "process_time": chat_time if 'chat_time' in locals() else 0
            },
            "document_parsing": {
                "success": parse_success,
                "process_time": parse_time if 'parse_time' in locals() else 0
            },
            "overall": {
                "success_rate": success_rate,
                "status": final_status,
                "recommendation": "dots.ocr готова к использованию" if success_rate >= 75 else "Требуется доработка"
            }
        }
        
        with open("dtype_fix_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в dtype_fix_test_results.json")
        
        return success_rate >= 50
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция."""
    try:
        success = test_dtype_fixed_dots_ocr()
        return success
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
        return False
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)