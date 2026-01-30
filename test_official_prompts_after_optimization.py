#!/usr/bin/env python3
"""
Тестирование официальных промптов dots.ocr после оптимизации токенов
"""

import requests
import base64
import time
import json
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

def create_test_image():
    """Создание тестового изображения с текстом и таблицей"""
    
    # Создаем изображение 800x600
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "ТЕСТОВЫЙ ДОКУМЕНТ", fill='black', font=font_large)
    
    # Обычный текст
    draw.text((50, 80), "Это тестовый документ для проверки официальных промптов dots.ocr.", fill='black', font=font_medium)
    draw.text((50, 110), "Документ содержит различные элементы для тестирования OCR.", fill='black', font=font_medium)
    
    # Таблица
    draw.text((50, 160), "ТАБЛИЦА ДАННЫХ:", fill='black', font=font_medium)
    
    # Рисуем таблицу
    table_x = 50
    table_y = 190
    cell_width = 120
    cell_height = 30
    
    # Заголовки таблицы
    headers = ["Название", "Количество", "Цена", "Сумма"]
    for i, header in enumerate(headers):
        x = table_x + i * cell_width
        y = table_y
        # Рамка
        draw.rectangle([x, y, x + cell_width, y + cell_height], outline='black', width=2)
        # Текст
        draw.text((x + 5, y + 5), header, fill='black', font=font_small)
    
    # Данные таблицы
    data = [
        ["Товар А", "10", "100", "1000"],
        ["Товар Б", "5", "200", "1000"],
        ["Товар В", "3", "300", "900"]
    ]
    
    for row_idx, row in enumerate(data):
        for col_idx, cell in enumerate(row):
            x = table_x + col_idx * cell_width
            y = table_y + (row_idx + 1) * cell_height
            # Рамка
            draw.rectangle([x, y, x + cell_width, y + cell_height], outline='black', width=1)
            # Текст
            draw.text((x + 5, y + 5), cell, fill='black', font=font_small)
    
    # Дополнительный текст
    draw.text((50, 350), "Дополнительная информация:", fill='black', font=font_medium)
    draw.text((50, 380), "• Пункт 1: Важная информация", fill='black', font=font_small)
    draw.text((50, 400), "• Пункт 2: Дополнительные данные", fill='black', font=font_small)
    draw.text((50, 420), "• Пункт 3: Заключительные замечания", fill='black', font=font_small)
    
    # Подпись
    draw.text((50, 500), "Документ создан для тестирования: " + datetime.now().strftime("%Y-%m-%d %H:%M"), fill='gray', font=font_small)
    
    return img

def test_official_prompts():
    """Тестирование всех официальных промптов dots.ocr"""
    
    print("🧪 ТЕСТИРОВАНИЕ ОФИЦИАЛЬНЫХ ПРОМПТОВ dots.ocr")
    print("=" * 60)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Проверка подключения к vLLM
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ vLLM сервер недоступен")
            return False
        print("✅ vLLM сервер работает")
    except Exception as e:
        print(f"❌ Ошибка подключения к vLLM: {e}")
        return False
    
    # Создание тестового изображения
    print("\n📷 Создание тестового изображения...")
    test_image = create_test_image()
    test_image.save("test_official_prompts_document.png")
    print("✅ Тестовое изображение создано: test_official_prompts_document.png")
    
    # Конвертация в base64
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Официальные промпты dots.ocr
    official_prompts = {
        "🔤 Простое OCR": {
            "prompt": "Extract all text from this image.",
            "description": "Извлекает весь текст включая таблицы в HTML"
        },
        "📋 Детальное OCR": {
            "prompt": "Extract all text content from this image while maintaining reading order. Exclude headers and footers.",
            "description": "Детальное извлечение с порядком чтения"
        },
        "🏗️ Анализ структуры": {
            "prompt": "Extract text, layout, and structure from this document image. Include bounding boxes, categories, and format tables as HTML, formulas as LaTeX, and text as Markdown.",
            "description": "Полный анализ макета и структуры"
        },
        "📊 Извлечение таблиц": {
            "prompt": "Extract and format the table content from this document as structured data.",
            "description": "Специально для табличных данных"
        },
        "📄 Структурированное извлечение": {
            "prompt": "Analyze this document and extract structured information including text, tables, and layout elements.",
            "description": "Комбинированный анализ документа"
        }
    }
    
    results = []
    
    print(f"\n🔍 Тестирование {len(official_prompts)} официальных промптов...")
    
    for prompt_name, prompt_info in official_prompts.items():
        print(f"\n   🧪 {prompt_name}")
        print(f"      Промпт: {prompt_info['prompt'][:50]}...")
        
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_info["prompt"]},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 4096,
            "temperature": 0.1
        }
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                json=payload,
                timeout=120
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                
                print(f"      ✅ Успех: {processing_time:.1f}с, токенов: {tokens_used}")
                print(f"      📄 Длина ответа: {len(content)} символов")
                
                # Проверяем качество ответа
                quality_indicators = {
                    "contains_table": "таблиц" in content.lower() or "table" in content.lower() or "<table>" in content,
                    "contains_structure": "структур" in content.lower() or "layout" in content.lower(),
                    "contains_text": len(content) > 100,
                    "different_from_simple": True  # Будем проверять позже
                }
                
                results.append({
                    "prompt_name": prompt_name,
                    "prompt": prompt_info["prompt"],
                    "success": True,
                    "processing_time": processing_time,
                    "tokens_used": tokens_used,
                    "response_length": len(content),
                    "response": content,
                    "quality": quality_indicators
                })
                
                # Показываем первые 200 символов ответа
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"      📝 Превью: {preview}")
                
            else:
                print(f"      ❌ Ошибка: {response.status_code}")
                print(f"         Ответ: {response.text[:100]}...")
                
                results.append({
                    "prompt_name": prompt_name,
                    "prompt": prompt_info["prompt"],
                    "success": False,
                    "error": response.status_code,
                    "error_text": response.text[:200]
                })
                
        except Exception as e:
            print(f"      ❌ Исключение: {e}")
            results.append({
                "prompt_name": prompt_name,
                "prompt": prompt_info["prompt"],
                "success": False,
                "error": "exception",
                "error_text": str(e)
            })
    
    return results

def analyze_results(results):
    """Анализ результатов тестирования"""
    
    print("\n" + "=" * 60)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
    print(f"   ✅ Успешных тестов: {len(successful_tests)}")
    print(f"   ❌ Неудачных тестов: {len(failed_tests)}")
    print(f"   📊 Процент успеха: {(len(successful_tests)/len(results)*100):.1f}%")
    
    if successful_tests:
        print(f"\n⏱️ ПРОИЗВОДИТЕЛЬНОСТЬ:")
        avg_time = sum(r["processing_time"] for r in successful_tests) / len(successful_tests)
        avg_tokens = sum(r["tokens_used"] for r in successful_tests) / len(successful_tests)
        avg_length = sum(r["response_length"] for r in successful_tests) / len(successful_tests)
        
        print(f"   ⏱️ Среднее время: {avg_time:.1f}с")
        print(f"   🎯 Средние токены: {avg_tokens:.0f}")
        print(f"   📄 Средняя длина: {avg_length:.0f} символов")
    
    # Проверка на одинаковые ответы
    if len(successful_tests) > 1:
        print(f"\n🔍 АНАЛИЗ УНИКАЛЬНОСТИ ОТВЕТОВ:")
        
        responses = [r["response"] for r in successful_tests]
        unique_responses = set(responses)
        
        if len(unique_responses) == 1:
            print("   ❌ ВСЕ ОТВЕТЫ ОДИНАКОВЫЕ! Проблема с официальными промптами!")
            print("   💡 dots.ocr игнорирует промпты и возвращает стандартный OCR")
        elif len(unique_responses) < len(responses) / 2:
            print("   ⚠️ Много повторяющихся ответов")
            print(f"   📊 Уникальных ответов: {len(unique_responses)} из {len(responses)}")
        else:
            print("   ✅ Ответы различаются - промпты работают корректно")
            print(f"   📊 Уникальных ответов: {len(unique_responses)} из {len(responses)}")
        
        # Показываем примеры различий
        print(f"\n📝 ПРИМЕРЫ ОТВЕТОВ:")
        for i, result in enumerate(successful_tests[:3]):
            preview = result["response"][:150] + "..." if len(result["response"]) > 150 else result["response"]
            print(f"   {i+1}. {result['prompt_name']}: {preview}")
    
    # Сохранение результатов
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": (len(successful_tests)/len(results)*100) if results else 0,
            "unique_responses": len(set(r["response"] for r in successful_tests)) if successful_tests else 0
        }
    }
    
    with open("official_prompts_test_after_optimization.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Подробный отчет сохранен: official_prompts_test_after_optimization.json")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    
    if len(successful_tests) == 0:
        print("   🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Ни один промпт не работает")
        print("   💡 Проверьте конфигурацию vLLM и модель dots.ocr")
    elif len(set(r["response"] for r in successful_tests)) == 1:
        print("   🚨 ПРОБЛЕМА: dots.ocr игнорирует промпты")
        print("   💡 Возможные причины:")
        print("      • Модель перезагружена без правильной конфигурации")
        print("      • Изменились параметры обработки промптов")
        print("      • Проблема с токенизацией после увеличения лимитов")
        print("   🔧 Решения:")
        print("      • Проверить параметры запуска vLLM")
        print("      • Убедиться в правильной передаче промптов")
        print("      • Протестировать с разными температурами")
    else:
        print("   ✅ Официальные промпты работают корректно")
        print("   🎯 Система готова к использованию")

def main():
    """Главная функция"""
    
    results = test_official_prompts()
    if results:
        analyze_results(results)

if __name__ == "__main__":
    main()