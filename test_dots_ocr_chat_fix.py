#!/usr/bin/env python3
"""
Тест исправлений для dots.ocr в режиме чата
Проверяем, что теперь модель дает адаптированные ответы на разные типы вопросов
"""

import os
import sys
import time
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import traceback

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

def create_test_image():
    """Создаем тестовое изображение с разным контентом."""
    img = Image.new('RGB', (500, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
    
    # Добавляем разнообразный контент
    draw.text((20, 30), "СЧЕТ № 12345", fill='black', font=font)
    draw.text((20, 60), "Дата: 24.01.2026", fill='black', font=font)
    draw.text((20, 90), "Сумма: 50,000 руб.", fill='black', font=font)
    draw.text((20, 120), "НДС: 9,000 руб.", fill='black', font=font)
    draw.text((20, 150), "Итого: 59,000 руб.", fill='black', font=font)
    draw.text((20, 180), "Плательщик: ООО Тест", fill='black', font=font)
    
    # Добавляем простую таблицу
    draw.rectangle([20, 220, 480, 280], outline='black', width=2)
    draw.line([20, 240, 480, 240], fill='black', width=1)
    draw.line([250, 220, 250, 280], fill='black', width=1)
    
    draw.text((30, 225), "Товар", fill='black', font=font)
    draw.text((260, 225), "Цена", fill='black', font=font)
    draw.text((30, 245), "Консультация", fill='black', font=font)
    draw.text((260, 245), "50,000 руб.", fill='black', font=font)
    
    return img

def test_improved_chat_responses():
    """Тестируем улучшенные ответы dots.ocr в режиме чата."""
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ dots.ocr В РЕЖИМЕ ЧАТА")
    print("=" * 60)
    
    try:
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        
        # Создаем адаптер
        adapter = VLLMStreamlitAdapter()
        
        # Создаем тестовое изображение
        test_image = create_test_image()
        test_image.save("test_dots_ocr_fix.png")
        print("📷 Создано тестовое изображение: test_dots_ocr_fix.png")
        
        # Тестируем разные типы вопросов с ожидаемыми улучшениями
        test_cases = [
            {
                "prompt": "Извлеки весь текст из изображения",
                "type": "OCR",
                "expected": "Должен вернуть полный текст как есть"
            },
            {
                "prompt": "Какие числа есть в документе?",
                "type": "NUMBER_SEARCH",
                "expected": "Должен найти и перечислить числа: 12345, 24, 01, 2026, 50000, 9000, 59000"
            },
            {
                "prompt": "Сколько слов в тексте?",
                "type": "WORD_COUNT",
                "expected": "Должен подсчитать примерное количество слов"
            },
            {
                "prompt": "Есть ли в документе текст?",
                "type": "TEXT_CHECK",
                "expected": "Должен подтвердить наличие текста и показать его"
            },
            {
                "prompt": "Что это за документ?",
                "type": "GENERAL",
                "expected": "Должен показать OCR + пояснение о специализации"
            },
            {
                "prompt": "Какого цвета фон?",
                "type": "COLOR",
                "expected": "Должен объяснить ограничения и предложить Qwen3-VL"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            prompt = test_case["prompt"]
            expected_type = test_case["type"]
            
            print(f"\n📝 Тест {i}: {prompt}")
            print(f"🎯 Ожидаемый тип: {expected_type}")
            print("-" * 40)
            
            try:
                start_time = time.time()
                
                # Отправляем запрос
                result = adapter.process_image(
                    image=test_image,
                    prompt=prompt,
                    model="rednote-hilab/dots.ocr"
                )
                
                processing_time = time.time() - start_time
                
                if result and result.get("success"):
                    response = result["text"]
                    print(f"✅ Успех ({processing_time:.2f}с)")
                    print(f"📄 Ответ: {response[:200]}{'...' if len(response) > 200 else ''}")
                    
                    # Анализируем качество ответа
                    analysis = analyze_response(prompt, response, expected_type)
                    
                    print(f"🔍 Анализ: {analysis['quality']} - {analysis['description']}")
                    
                    results.append({
                        "prompt": prompt,
                        "expected_type": expected_type,
                        "response": response,
                        "processing_time": processing_time,
                        "analysis": analysis,
                        "success": True
                    })
                    
                else:
                    print("❌ Ошибка обработки")
                    results.append({
                        "prompt": prompt,
                        "expected_type": expected_type,
                        "error": "Processing failed",
                        "success": False
                    })
                
            except Exception as e:
                print(f"❌ Исключение: {e}")
                results.append({
                    "prompt": prompt,
                    "expected_type": expected_type,
                    "error": str(e),
                    "success": False
                })
        
        # Сохраняем результаты
        with open("dots_ocr_chat_fix_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Анализ улучшений
        print("\n" + "=" * 60)
        print("📊 АНАЛИЗ УЛУЧШЕНИЙ")
        print("=" * 60)
        
        successful_tests = [r for r in results if r.get("success")]
        improved_responses = [r for r in successful_tests if r.get("analysis", {}).get("improved", False)]
        
        print(f"✅ Успешных тестов: {len(successful_tests)}/{len(results)}")
        print(f"🎯 Улучшенных ответов: {len(improved_responses)}")
        
        # Детальный анализ по типам
        for test_type in ["OCR", "NUMBER_SEARCH", "WORD_COUNT", "TEXT_CHECK", "GENERAL", "COLOR"]:
            type_results = [r for r in successful_tests if r.get("expected_type") == test_type]
            if type_results:
                result = type_results[0]
                quality = result.get("analysis", {}).get("quality", "UNKNOWN")
                print(f"  • {test_type}: {quality}")
        
        return results
        
    except ImportError:
        print("❌ vLLM адаптер недоступен")
        return None
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def analyze_response(prompt, response, expected_type):
    """Анализируем качество ответа в зависимости от типа вопроса."""
    
    # Проверяем, является ли это просто полным OCR
    is_full_ocr = ("СЧЕТ" in response and "Дата" in response and "Сумма" in response)
    
    if expected_type == "OCR":
        # Для OCR вопросов полный текст - это хорошо
        if is_full_ocr:
            return {
                "quality": "ОТЛИЧНО",
                "description": "Корректное полное OCR",
                "improved": True
            }
        else:
            return {
                "quality": "ПЛОХО",
                "description": "Неполное OCR",
                "improved": False
            }
    
    elif expected_type == "NUMBER_SEARCH":
        # Для поиска чисел ожидаем специфический ответ
        if "найдены числа" in response.lower() or "числа:" in response.lower():
            return {
                "quality": "ОТЛИЧНО",
                "description": "Специфический ответ на поиск чисел",
                "improved": True
            }
        elif is_full_ocr and not ("найдены" in response.lower()):
            return {
                "quality": "ПЛОХО",
                "description": "Полное OCR вместо поиска чисел",
                "improved": False
            }
        else:
            return {
                "quality": "СРЕДНЕ",
                "description": "Частично адаптированный ответ",
                "improved": True
            }
    
    elif expected_type == "WORD_COUNT":
        # Для подсчета слов ожидаем число
        if "слов" in response.lower() and any(char.isdigit() for char in response):
            return {
                "quality": "ОТЛИЧНО",
                "description": "Подсчет слов выполнен",
                "improved": True
            }
        elif is_full_ocr:
            return {
                "quality": "ПЛОХО",
                "description": "Полное OCR вместо подсчета",
                "improved": False
            }
        else:
            return {
                "quality": "СРЕДНЕ",
                "description": "Частичный ответ",
                "improved": True
            }
    
    elif expected_type == "TEXT_CHECK":
        # Для проверки наличия текста
        if "да" in response.lower() and "текст" in response.lower():
            return {
                "quality": "ОТЛИЧНО",
                "description": "Подтверждение наличия текста",
                "improved": True
            }
        elif is_full_ocr:
            return {
                "quality": "СРЕДНЕ",
                "description": "Показал текст, но не ответил на вопрос",
                "improved": False
            }
        else:
            return {
                "quality": "ПЛОХО",
                "description": "Неясный ответ",
                "improved": False
            }
    
    elif expected_type == "COLOR":
        # Для вопросов о цвете ожидаем объяснение ограничений
        if "qwen" in response.lower() or "специализирована" in response.lower():
            return {
                "quality": "ОТЛИЧНО",
                "description": "Объяснение ограничений и рекомендации",
                "improved": True
            }
        elif is_full_ocr:
            return {
                "quality": "ПЛОХО",
                "description": "Полное OCR вместо объяснения",
                "improved": False
            }
        else:
            return {
                "quality": "СРЕДНЕ",
                "description": "Частичное объяснение",
                "improved": True
            }
    
    elif expected_type == "GENERAL":
        # Для общих вопросов ожидаем OCR + пояснение
        if ("специализирована" in response.lower() or "qwen" in response.lower()) and is_full_ocr:
            return {
                "quality": "ОТЛИЧНО",
                "description": "OCR + пояснение о специализации",
                "improved": True
            }
        elif is_full_ocr:
            return {
                "quality": "СРЕДНЕ",
                "description": "Только OCR без пояснений",
                "improved": False
            }
        else:
            return {
                "quality": "ПЛОХО",
                "description": "Неполный ответ",
                "improved": False
            }
    
    return {
        "quality": "НЕИЗВЕСТНО",
        "description": "Не удалось проанализировать",
        "improved": False
    }

def main():
    """Основная функция тестирования исправлений."""
    print("🔧 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ dots.ocr В РЕЖИМЕ ЧАТА")
    print("=" * 80)
    
    # Тестируем улучшенные ответы
    results = test_improved_chat_responses()
    
    if results:
        # Итоговый отчет
        print("\n" + "=" * 80)
        print("📋 ИТОГОВЫЙ ОТЧЕТ ОБ ИСПРАВЛЕНИЯХ")
        print("=" * 80)
        
        successful_tests = [r for r in results if r.get("success")]
        improved_responses = [r for r in successful_tests if r.get("analysis", {}).get("improved", False)]
        
        improvement_rate = len(improved_responses) / len(successful_tests) * 100 if successful_tests else 0
        
        print(f"✅ Успешных тестов: {len(successful_tests)}/{len(results)}")
        print(f"🎯 Улучшенных ответов: {len(improved_responses)}")
        print(f"📈 Процент улучшений: {improvement_rate:.1f}%")
        
        if improvement_rate >= 70:
            print("\n🎉 ИСПРАВЛЕНИЯ РАБОТАЮТ ОТЛИЧНО!")
            print("   dots.ocr теперь дает адаптированные ответы на разные типы вопросов")
        elif improvement_rate >= 40:
            print("\n✅ ИСПРАВЛЕНИЯ ЧАСТИЧНО РАБОТАЮТ")
            print("   Есть улучшения, но требуется дополнительная настройка")
        else:
            print("\n❌ ИСПРАВЛЕНИЯ НЕ РАБОТАЮТ")
            print("   Требуется пересмотр подхода к адаптации ответов")
        
        # Сохраняем итоговый отчет
        final_report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": results,
            "summary": {
                "total_tests": len(results),
                "successful_tests": len(successful_tests),
                "improved_responses": len(improved_responses),
                "improvement_rate": improvement_rate
            }
        }
        
        with open("dots_ocr_chat_fix_report.json", "w", encoding="utf-8") as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Полный отчет сохранен в dots_ocr_chat_fix_report.json")

if __name__ == "__main__":
    main()