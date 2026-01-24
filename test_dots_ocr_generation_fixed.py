#!/usr/bin/env python3
"""
ТЕСТ GENERATION-ИСПРАВЛЕННОЙ DOTS.OCR

Проверяем исправление всех проблем:
1. Dtype mismatch (BFloat16/Half) 
2. Генерация повторяющихся символов
3. Правильное извлечение текста
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
    draw.text((50, 30), "GENERATION FIX TEST", fill='black', font=title_font)
    
    # Основная информация
    draw.text((50, 80), "Document ID: GEN-FIX-2026", fill='black', font=font)
    draw.text((50, 110), "Date: January 24, 2026", fill='black', font=font)
    draw.text((50, 140), "Status: TESTING", fill='black', font=font)
    draw.text((50, 170), "Purpose: Fix generation issues", fill='black', font=font)
    
    # Дополнительный текст
    draw.text((50, 220), "Expected Results:", fill='black', font=font)
    draw.text((50, 250), "• No repetitive symbols", fill='black', font=font)
    draw.text((50, 280), "• Proper text extraction", fill='black', font=font)
    draw.text((50, 310), "• Fast processing", fill='black', font=font)
    
    # Сохраняем для визуального контроля
    img.save("test_generation_fix_document.png")
    
    return img

def test_generation_fixed_dots_ocr():
    """Тестируем generation-исправленную dots.ocr."""
    print("🚀 ТЕСТ GENERATION-ИСПРАВЛЕННОЙ DOTS.OCR")
    print("=" * 50)
    
    try:
        from models.model_loader import ModelLoader
        
        # Создаем тестовое изображение
        test_image = create_test_document()
        
        # Загружаем generation-исправленную модель
        print("📥 Загружаем generation-исправленную dots.ocr...")
        start_load = time.time()
        
        model = ModelLoader.load_model("dots_ocr")  # Теперь автоматически использует generation-fixed версию
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
            dtype_error = "BFloat16" in result or "Half" in result
            print(f"{'❌' if dtype_error else '✅'} Dtype ошибка: {'Присутствует' if dtype_error else 'Исправлена'}")
            
            # Проверяем на повторяющиеся символы
            repetitive_symbols = any(char * 5 in result for char in "!@#$%^&*()_+-=[]{}|;':\",./<>?")
            print(f"{'❌' if repetitive_symbols else '✅'} Повторяющиеся символы: {'Найдены' if repetitive_symbols else 'Отсутствуют'}")
            
            # Анализируем качество
            expected_keywords = ["GENERATION", "FIX", "TEST", "GEN-FIX-2026", "TESTING", "January"]
            found_keywords = sum(1 for kw in expected_keywords if kw.upper() in result.upper())
            quality_score = (found_keywords / len(expected_keywords)) * 100
            
            print(f"🎯 Качество OCR: {found_keywords}/{len(expected_keywords)} ({quality_score:.1f}%)")
            
            test1_success = not dtype_error and not repetitive_symbols and quality_score > 0
            
        except Exception as e:
            print(f"❌ Ошибка в тесте 1: {e}")
            test1_success = False
            dtype_error = "BFloat16" in str(e) or "Half" in str(e)
            repetitive_symbols = False
            quality_score = 0
            process_time = 0
        
        # Тест 2: Чат с моделью
        print("\n🔍 Тест 2: Чат с моделью")
        start_chat = time.time()
        
        try:
            chat_result = model.chat(test_image, "What is the document ID in this image?")
            chat_time = time.time() - start_chat
            
            print(f"⏱️ Время чата: {chat_time:.3f}s")
            print(f"💬 Ответ чата: {chat_result[:150]}...")
            
            # Проверяем, содержит ли ответ ID документа
            chat_success = "GEN-FIX-2026" in chat_result.upper()
            chat_no_repetition = not any(char * 5 in chat_result for char in "!@#$%^&*()_+-=[]{}|;':\",./<>?")
            
            print(f"🎯 Чат успешен: {'✅' if chat_success else '❌'}")
            print(f"🎯 Без повторений: {'✅' if chat_no_repetition else '❌'}")
            
            chat_overall_success = chat_success and chat_no_repetition
            
        except Exception as e:
            print(f"❌ Ошибка в тесте 2: {e}")
            chat_overall_success = False
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
            parse_text = parsed_result.get('text', '')
            parse_no_repetition = not any(char * 5 in parse_text for char in "!@#$%^&*()_+-=[]{}|;':\",./<>?")
            
            print(f"🎯 Без повторений в парсинге: {'✅' if parse_no_repetition else '❌'}")
            
            parse_overall_success = parse_success and parse_no_repetition
            
        except Exception as e:
            print(f"❌ Ошибка в тесте 3: {e}")
            parse_overall_success = False
            parse_time = 0
        
        # Тест 4: Стресс-тест на разных промптах
        print("\n🔍 Тест 4: Стресс-тест разных промптов")
        stress_results = []
        
        test_prompts = [
            "Read all text",
            "Extract text content",
            "What do you see?",
            "Perform OCR",
            "List all text elements"
        ]
        
        for i, prompt in enumerate(test_prompts):
            try:
                start_stress = time.time()
                stress_result = model.chat(test_image, prompt)
                stress_time = time.time() - start_stress
                
                # Проверяем качество результата
                has_repetition = any(char * 5 in stress_result for char in "!@#$%^&*()_+-=[]{}|;':\",./<>?")
                has_content = len(stress_result.strip()) > 10 and len(set(stress_result.replace(' ', ''))) > 5
                
                stress_success = not has_repetition and has_content
                stress_results.append(stress_success)
                
                print(f"   Промпт {i+1}: {'✅' if stress_success else '❌'} ({stress_time:.2f}s)")
                
            except Exception as e:
                print(f"   Промпт {i+1}: ❌ Ошибка: {e}")
                stress_results.append(False)
        
        stress_success_rate = (sum(stress_results) / len(stress_results)) * 100
        print(f"🎯 Стресс-тест: {sum(stress_results)}/{len(stress_results)} ({stress_success_rate:.1f}%)")
        
        # Выгружаем модель
        model.unload()
        
        # Итоговый анализ
        print("\n" + "=" * 50)
        print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ GENERATION FIX")
        print("=" * 50)
        
        print(f"✅ Загрузка модели: {load_time:.2f}s")
        print(f"{'✅' if test1_success else '❌'} Извлечение текста: {quality_score:.1f}% качество")
        print(f"{'✅' if not dtype_error else '❌'} Dtype ошибка: {'Исправлена' if not dtype_error else 'Присутствует'}")
        print(f"{'✅' if chat_overall_success else '❌'} Чат функция: {'Работает' if chat_overall_success else 'Не работает'}")
        print(f"{'✅' if parse_overall_success else '❌'} Парсинг документа: {'Работает' if parse_overall_success else 'Не работает'}")
        print(f"{'✅' if stress_success_rate >= 60 else '❌'} Стресс-тест: {stress_success_rate:.1f}%")
        
        # Общая оценка
        total_tests = 5  # загрузка, извлечение, чат, парсинг, стресс-тест
        passed_tests = sum([
            True,  # загрузка всегда успешна если дошли до сюда
            test1_success,
            chat_overall_success,
            parse_overall_success,
            stress_success_rate >= 60
        ])
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {passed_tests}/{total_tests} тестов пройдено ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 GENERATION FIX РАБОТАЕТ ОТЛИЧНО!")
            final_status = "excellent"
        elif success_rate >= 60:
            print("✅ Generation fix работает хорошо")
            final_status = "good"
        elif success_rate >= 40:
            print("⚠️ Generation fix работает удовлетворительно")
            final_status = "satisfactory"
        else:
            print("❌ Требуется дополнительная доработка")
            final_status = "needs_work"
        
        # Сохраняем результаты
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_class": model.__class__.__name__,
            "load_time": load_time,
            "dtype_error_fixed": not dtype_error,
            "repetition_fixed": not repetitive_symbols if 'repetitive_symbols' in locals() else True,
            "text_extraction": {
                "success": test1_success,
                "quality_score": quality_score,
                "process_time": process_time
            },
            "chat_function": {
                "success": chat_overall_success,
                "process_time": chat_time if 'chat_time' in locals() else 0
            },
            "document_parsing": {
                "success": parse_overall_success,
                "process_time": parse_time if 'parse_time' in locals() else 0
            },
            "stress_test": {
                "success_rate": stress_success_rate,
                "passed": sum(stress_results),
                "total": len(stress_results)
            },
            "overall": {
                "success_rate": success_rate,
                "status": final_status,
                "recommendation": "dots.ocr готова к использованию" if success_rate >= 60 else "Требуется доработка"
            }
        }
        
        with open("generation_fix_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в generation_fix_test_results.json")
        
        return success_rate >= 60
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция."""
    try:
        success = test_generation_fixed_dots_ocr()
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