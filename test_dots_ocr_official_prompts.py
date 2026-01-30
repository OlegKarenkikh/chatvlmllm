#!/usr/bin/env python3
"""
Тестирование официальных промптов dots.ocr из документации
Проверяем, что официальные промпты работают корректно
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

def create_comprehensive_test_document():
    """Создаем комплексный тестовый документ с разными элементами."""
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        header_font = ImageFont.truetype("arial.ttf", 18)
        text_font = ImageFont.truetype("arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    y_pos = 30
    
    # Заголовок документа
    draw.text((50, y_pos), "СЧЕТ-ФАКТУРА № 12345", fill='black', font=title_font)
    y_pos += 40
    
    # Дата и основная информация
    draw.text((50, y_pos), "Дата: 24 января 2026 г.", fill='black', font=header_font)
    y_pos += 30
    draw.text((50, y_pos), "Поставщик: ООО 'Технологии Будущего'", fill='black', font=text_font)
    y_pos += 25
    draw.text((50, y_pos), "ИНН: 7702123456, КПП: 770201001", fill='black', font=text_font)
    y_pos += 25
    draw.text((50, y_pos), "Адрес: 119991, г. Москва, ул. Ленинский пр-т, д. 1", fill='black', font=text_font)
    y_pos += 40
    
    draw.text((50, y_pos), "Покупатель: ООО 'Инновационные Решения'", fill='black', font=text_font)
    y_pos += 25
    draw.text((50, y_pos), "ИНН: 7703654321, КПП: 770301001", fill='black', font=text_font)
    y_pos += 50
    
    # Таблица товаров
    table_start_y = y_pos
    
    # Заголовок таблицы
    draw.rectangle([50, y_pos, 750, y_pos + 30], outline='black', width=2, fill='lightgray')
    draw.text((60, y_pos + 8), "№", fill='black', font=text_font)
    draw.text((100, y_pos + 8), "Наименование товара", fill='black', font=text_font)
    draw.text((400, y_pos + 8), "Кол-во", fill='black', font=text_font)
    draw.text((500, y_pos + 8), "Цена", fill='black', font=text_font)
    draw.text((600, y_pos + 8), "Сумма", fill='black', font=text_font)
    y_pos += 30
    
    # Строки таблицы
    items = [
        ("1", "Программное обеспечение", "1 шт", "50,000.00", "50,000.00"),
        ("2", "Техническая поддержка", "12 мес", "5,000.00", "60,000.00"),
        ("3", "Обучение персонала", "1 курс", "15,000.00", "15,000.00")
    ]
    
    for item in items:
        draw.rectangle([50, y_pos, 750, y_pos + 25], outline='black', width=1)
        draw.text((60, y_pos + 5), item[0], fill='black', font=text_font)
        draw.text((100, y_pos + 5), item[1], fill='black', font=text_font)
        draw.text((400, y_pos + 5), item[2], fill='black', font=text_font)
        draw.text((500, y_pos + 5), item[3], fill='black', font=text_font)
        draw.text((600, y_pos + 5), item[4], fill='black', font=text_font)
        y_pos += 25
    
    # Итоговая строка
    draw.rectangle([50, y_pos, 750, y_pos + 30], outline='black', width=2, fill='lightblue')
    draw.text((400, y_pos + 8), "ИТОГО:", fill='black', font=header_font)
    draw.text((600, y_pos + 8), "125,000.00 руб.", fill='black', font=header_font)
    y_pos += 50
    
    # НДС информация
    draw.text((50, y_pos), "НДС 20%: 25,000.00 руб.", fill='black', font=text_font)
    y_pos += 25
    draw.text((50, y_pos), "Всего к оплате: 150,000.00 руб.", fill='black', font=header_font)
    y_pos += 50
    
    # Подписи
    draw.text((50, y_pos), "Руководитель: _________________ И.И. Иванов", fill='black', font=text_font)
    y_pos += 30
    draw.text((50, y_pos), "Главный бухгалтер: ____________ П.П. Петров", fill='black', font=text_font)
    y_pos += 50
    
    # Математическая формула (для тестирования)
    draw.text((50, y_pos), "Формула расчета: S = P × (1 + r)^n", fill='black', font=text_font)
    y_pos += 25
    draw.text((50, y_pos), "где S - итоговая сумма, P - основная сумма, r - ставка, n - период", fill='black', font=text_font)
    
    return img

def test_official_dots_ocr_prompts():
    """Тестируем официальные промпты dots.ocr."""
    print("🧪 ТЕСТИРОВАНИЕ ОФИЦИАЛЬНЫХ ПРОМПТОВ dots.ocr")
    print("=" * 60)
    
    try:
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        
        # Создаем адаптер
        adapter = VLLMStreamlitAdapter()
        
        # Создаем комплексное тестовое изображение
        test_image = create_comprehensive_test_document()
        test_image.save("test_dots_ocr_official_document.png")
        print("📷 Создан комплексный тестовый документ: test_dots_ocr_official_document.png")
        
        # Официальные промпты из документации dots.ocr
        official_prompts = {
            "prompt_layout_all_en": {
                "prompt": "Extract text, layout, and structure from this document image. Include bounding boxes, categories, and format tables as HTML, formulas as LaTeX, and text as Markdown.",
                "description": "Полный анализ документа с макетом и структурой",
                "expected": "Структурированный JSON с bbox, категориями, HTML таблицами"
            },
            
            "prompt_layout_only_en": {
                "prompt": "Detect and extract only the layout elements and their positions in this document image. Return bounding boxes and categories without text extraction.",
                "description": "Только детекция макета без извлечения текста",
                "expected": "JSON с bbox и категориями элементов"
            },
            
            "prompt_ocr": {
                "prompt": "Extract all text content from this image while maintaining reading order. Exclude headers and footers.",
                "description": "Простое извлечение текста с сохранением порядка чтения",
                "expected": "Чистый текст без заголовков и подвалов"
            },
            
            "prompt_grounding_ocr": {
                "prompt": "Extract text from the specified region [50, 100, 400, 200] in this image.",
                "description": "Извлечение текста из указанной области",
                "expected": "Текст только из указанного региона"
            },
            
            # Дополнительные промпты для тестирования
            "simple_ocr": {
                "prompt": "Extract all text from this image.",
                "description": "Базовое извлечение текста",
                "expected": "Весь текст с изображения"
            },
            
            "table_extraction": {
                "prompt": "Extract and format the table content from this document as structured data.",
                "description": "Извлечение таблиц",
                "expected": "Структурированные данные таблицы"
            }
        }
        
        results = []
        
        for prompt_name, prompt_info in official_prompts.items():
            prompt_text = prompt_info["prompt"]
            description = prompt_info["description"]
            
            print(f"\n📝 Тест: {prompt_name}")
            print(f"📋 Описание: {description}")
            print(f"🎯 Промпт: {prompt_text[:80]}{'...' if len(prompt_text) > 80 else ''}")
            print("-" * 50)
            
            try:
                start_time = time.time()
                
                # Отправляем запрос с официальным промптом
                result = adapter.process_image(
                    image=test_image,
                    prompt=prompt_text,
                    model="rednote-hilab/dots.ocr"
                )
                
                processing_time = time.time() - start_time
                
                if result and result.get("success"):
                    response = result["text"]
                    print(f"✅ Успех ({processing_time:.2f}с)")
                    print(f"📄 Длина ответа: {len(response)} символов")
                    print(f"📄 Начало ответа: {response[:200]}{'...' if len(response) > 200 else ''}")
                    
                    # Анализируем качество ответа
                    analysis = analyze_official_response(prompt_name, response)
                    print(f"🔍 Анализ: {analysis['quality']} - {analysis['description']}")
                    
                    results.append({
                        "prompt_name": prompt_name,
                        "prompt": prompt_text,
                        "description": description,
                        "response": response,
                        "response_length": len(response),
                        "processing_time": processing_time,
                        "analysis": analysis,
                        "success": True
                    })
                    
                else:
                    print("❌ Ошибка обработки")
                    results.append({
                        "prompt_name": prompt_name,
                        "prompt": prompt_text,
                        "description": description,
                        "error": "Processing failed",
                        "success": False
                    })
                
            except Exception as e:
                print(f"❌ Исключение: {e}")
                results.append({
                    "prompt_name": prompt_name,
                    "prompt": prompt_text,
                    "description": description,
                    "error": str(e),
                    "success": False
                })
        
        # Сохраняем результаты
        with open("dots_ocr_official_prompts_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Анализ результатов
        print("\n" + "=" * 60)
        print("📊 АНАЛИЗ ОФИЦИАЛЬНЫХ ПРОМПТОВ")
        print("=" * 60)
        
        successful_tests = [r for r in results if r.get("success")]
        high_quality = [r for r in successful_tests if r.get("analysis", {}).get("quality") == "ОТЛИЧНО"]
        
        print(f"✅ Успешных тестов: {len(successful_tests)}/{len(results)}")
        print(f"🎯 Высокое качество: {len(high_quality)}")
        
        # Детальный анализ по промптам
        for result in successful_tests:
            prompt_name = result["prompt_name"]
            quality = result.get("analysis", {}).get("quality", "НЕИЗВЕСТНО")
            length = result["response_length"]
            time_taken = result["processing_time"]
            print(f"  • {prompt_name}: {quality} ({length} символов, {time_taken:.2f}с)")
        
        return results
        
    except ImportError:
        print("❌ vLLM адаптер недоступен")
        return None
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def analyze_official_response(prompt_name, response):
    """Анализируем качество ответа для официальных промптов."""
    
    if prompt_name == "prompt_layout_all_en":
        # Ожидаем структурированный вывод с макетом
        if any(marker in response.lower() for marker in ['<table', 'bbox', 'category', 'layout']):
            return {
                "quality": "ОТЛИЧНО",
                "description": "Структурированный вывод с макетом",
                "structured": True
            }
        elif len(response) > 500:
            return {
                "quality": "ХОРОШО",
                "description": "Подробный ответ, возможно структурированный",
                "structured": True
            }
        else:
            return {
                "quality": "СРЕДНЕ",
                "description": "Короткий ответ, недостаточно структуры",
                "structured": False
            }
    
    elif prompt_name == "prompt_layout_only_en":
        # Ожидаем только информацию о макете
        if any(marker in response.lower() for marker in ['bbox', 'position', 'layout', 'element']):
            return {
                "quality": "ОТЛИЧНО",
                "description": "Информация о макете найдена",
                "structured": True
            }
        else:
            return {
                "quality": "ПЛОХО",
                "description": "Нет информации о макете",
                "structured": False
            }
    
    elif prompt_name == "prompt_ocr":
        # Ожидаем чистый текст
        has_text_content = any(word in response for word in ['СЧЕТ', 'Дата', 'Поставщик', 'руб'])
        no_html_tags = '<' not in response and '>' not in response
        
        if has_text_content and no_html_tags:
            return {
                "quality": "ОТЛИЧНО",
                "description": "Чистый текст без разметки",
                "structured": False
            }
        elif has_text_content:
            return {
                "quality": "ХОРОШО",
                "description": "Текст извлечен, но есть разметка",
                "structured": True
            }
        else:
            return {
                "quality": "ПЛОХО",
                "description": "Текст не извлечен корректно",
                "structured": False
            }
    
    elif prompt_name == "prompt_grounding_ocr":
        # Ожидаем текст из указанной области
        if len(response) > 0 and len(response) < 200:
            return {
                "quality": "ОТЛИЧНО",
                "description": "Текст из указанной области",
                "structured": False
            }
        elif len(response) > 200:
            return {
                "quality": "СРЕДНЕ",
                "description": "Слишком много текста для области",
                "structured": False
            }
        else:
            return {
                "quality": "ПЛОХО",
                "description": "Нет текста из области",
                "structured": False
            }
    
    elif prompt_name == "simple_ocr":
        # Базовое OCR
        has_content = len(response) > 100
        has_key_words = any(word in response for word in ['СЧЕТ', 'руб', 'ООО'])
        
        if has_content and has_key_words:
            return {
                "quality": "ОТЛИЧНО",
                "description": "Полное извлечение текста",
                "structured": False
            }
        else:
            return {
                "quality": "СРЕДНЕ",
                "description": "Частичное извлечение",
                "structured": False
            }
    
    elif prompt_name == "table_extraction":
        # Извлечение таблиц
        if any(marker in response.lower() for marker in ['<table', 'программное', 'поддержка', '50,000']):
            return {
                "quality": "ОТЛИЧНО",
                "description": "Таблица извлечена",
                "structured": True
            }
        else:
            return {
                "quality": "СРЕДНЕ",
                "description": "Частичное извлечение таблицы",
                "structured": False
            }
    
    return {
        "quality": "НЕИЗВЕСТНО",
        "description": "Не удалось проанализировать",
        "structured": False
    }

def main():
    """Основная функция тестирования официальных промптов."""
    print("🔬 ТЕСТИРОВАНИЕ ОФИЦИАЛЬНЫХ ПРОМПТОВ dots.ocr")
    print("=" * 80)
    
    # Тестируем официальные промпты
    results = test_official_dots_ocr_prompts()
    
    if results:
        # Итоговый отчет
        print("\n" + "=" * 80)
        print("📋 ИТОГОВЫЙ ОТЧЕТ ПО ОФИЦИАЛЬНЫМ ПРОМПТАМ")
        print("=" * 80)
        
        successful_tests = [r for r in results if r.get("success")]
        high_quality = [r for r in successful_tests if r.get("analysis", {}).get("quality") == "ОТЛИЧНО"]
        structured_responses = [r for r in successful_tests if r.get("analysis", {}).get("structured", False)]
        
        success_rate = len(successful_tests) / len(results) * 100 if results else 0
        quality_rate = len(high_quality) / len(successful_tests) * 100 if successful_tests else 0
        
        print(f"✅ Успешность: {len(successful_tests)}/{len(results)} ({success_rate:.1f}%)")
        print(f"🎯 Высокое качество: {len(high_quality)}/{len(successful_tests)} ({quality_rate:.1f}%)")
        print(f"📊 Структурированные ответы: {len(structured_responses)}")
        
        if success_rate >= 80 and quality_rate >= 60:
            print("\n🎉 ОФИЦИАЛЬНЫЕ ПРОМПТЫ РАБОТАЮТ ОТЛИЧНО!")
            print("   dots.ocr корректно обрабатывает официальные промпты")
            success_status = True
        elif success_rate >= 60:
            print("\n✅ ОФИЦИАЛЬНЫЕ ПРОМПТЫ ЧАСТИЧНО РАБОТАЮТ")
            print("   Большинство промптов работает, есть области для улучшения")
            success_status = True
        else:
            print("\n❌ ПРОБЛЕМЫ С ОФИЦИАЛЬНЫМИ ПРОМПТАМИ")
            print("   Требуется диагностика и исправления")
            success_status = False
        
        # Рекомендации
        print("\n💡 РЕКОМЕНДАЦИИ:")
        if success_status:
            print("1. Используйте официальные промпты для лучших результатов")
            print("2. prompt_ocr - для простого извлечения текста")
            print("3. prompt_layout_all_en - для структурированного анализа")
            print("4. Избегайте произвольных промптов в чате")
        else:
            print("1. Проверьте конфигурацию vLLM сервера")
            print("2. Убедитесь в корректности модели dots.ocr")
            print("3. Рассмотрите использование других OCR моделей")
        
        # Сохраняем итоговый отчет
        final_report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": results,
            "summary": {
                "total_tests": len(results),
                "successful_tests": len(successful_tests),
                "high_quality_responses": len(high_quality),
                "structured_responses": len(structured_responses),
                "success_rate": success_rate,
                "quality_rate": quality_rate,
                "overall_success": success_status
            },
            "recommendations": {
                "use_official_prompts": True,
                "best_prompts": ["prompt_ocr", "prompt_layout_all_en"],
                "avoid_arbitrary_chat": True
            }
        }
        
        with open("dots_ocr_official_prompts_report.json", "w", encoding="utf-8") as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Полный отчет сохранен в dots_ocr_official_prompts_report.json")
        
        return success_status
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    else:
        print("\n❌ ТЕСТИРОВАНИЕ ВЫЯВИЛО ПРОБЛЕМЫ")