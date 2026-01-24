#!/usr/bin/env python3
"""
Тестирование исправления официальных промптов в интерфейсе
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
    draw.text((50, 30), "ТЕСТ ИСПРАВЛЕНИЯ ОФИЦИАЛЬНЫХ ПРОМПТОВ", fill='black', font=font_large)
    
    # Обычный текст
    draw.text((50, 80), "Этот документ создан для проверки исправления официальных промптов.", fill='black', font=font_medium)
    draw.text((50, 110), "Каждый промпт должен давать уникальный результат.", fill='black', font=font_medium)
    
    # Таблица
    draw.text((50, 160), "ТАБЛИЦА ДЛЯ ТЕСТИРОВАНИЯ:", fill='black', font=font_medium)
    
    # Рисуем таблицу
    table_x = 50
    table_y = 190
    cell_width = 120
    cell_height = 30
    
    # Заголовки таблицы
    headers = ["Промпт", "Статус", "Токены", "Результат"]
    for i, header in enumerate(headers):
        x = table_x + i * cell_width
        y = table_y
        # Рамка
        draw.rectangle([x, y, x + cell_width, y + cell_height], outline='black', width=2)
        # Текст
        draw.text((x + 5, y + 5), header, fill='black', font=font_small)
    
    # Данные таблицы
    data = [
        ["Простое OCR", "OK", "~800", "Полный текст"],
        ["Детальное OCR", "OK", "~900", "С порядком"],
        ["Анализ структуры", "OK", "~950", "HTML + Markdown"],
        ["Извлечение таблиц", "OK", "~1000", "Только таблицы"],
        ["Структурированное", "OK", "~850", "Комбинированный"]
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
    draw.text((50, 350), "Проверяемые аспекты:", fill='black', font=font_medium)
    draw.text((50, 380), "• Корректная передача промптов в vLLM API", fill='black', font=font_small)
    draw.text((50, 400), "• Правильный расчет лимитов токенов", fill='black', font=font_small)
    draw.text((50, 420), "• Уникальность ответов для разных промптов", fill='black', font=font_small)
    draw.text((50, 440), "• Отсутствие ошибок валидации токенов", fill='black', font=font_small)
    
    # Подпись
    draw.text((50, 500), "Тест создан: " + datetime.now().strftime("%Y-%m-%d %H:%M"), fill='gray', font=font_small)
    
    return img

def test_token_calculation():
    """Тестирование расчета токенов"""
    
    print("🧮 ТЕСТИРОВАНИЕ РАСЧЕТА ТОКЕНОВ")
    print("=" * 50)
    
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
    
    # Получение информации о модели
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            for model in models_data.get("data", []):
                if "dots.ocr" in model["id"]:
                    model_max_tokens = model.get("max_model_len", 1024)
                    print(f"📊 Модель: {model['id']}")
                    print(f"🎯 Максимум токенов: {model_max_tokens}")
                    break
        else:
            print("❌ Не удалось получить информацию о модели")
            return False
    except Exception as e:
        print(f"❌ Ошибка получения информации о модели: {e}")
        return False
    
    # Тестирование различных значений токенов
    test_cases = [
        {"requested": 8192, "description": "Максимальное значение"},
        {"requested": 7500, "description": "Близко к максимуму"},
        {"requested": 4096, "description": "Стандартное значение"},
        {"requested": 2048, "description": "Безопасное значение"},
        {"requested": 1024, "description": "Минимальное значение"}
    ]
    
    print(f"\n🧪 Тестирование различных лимитов токенов:")
    
    for case in test_cases:
        requested = case["requested"]
        description = case["description"]
        
        # Расчет безопасного лимита (как в исправленном коде)
        safe_max_tokens = min(requested, model_max_tokens - 500)  # Резерв для входных токенов
        
        if safe_max_tokens < 100:
            safe_max_tokens = model_max_tokens // 2
        
        print(f"   📝 {description}:")
        print(f"      Запрошено: {requested}")
        print(f"      Безопасно: {safe_max_tokens}")
        print(f"      Статус: {'✅ OK' if safe_max_tokens > 0 else '❌ Ошибка'}")
    
    return True

def test_official_prompts_with_safe_tokens():
    """Тестирование официальных промптов с безопасными токенами"""
    
    print("\n🎯 ТЕСТИРОВАНИЕ ОФИЦИАЛЬНЫХ ПРОМПТОВ С ИСПРАВЛЕНИЕМ")
    print("=" * 60)
    
    # Создание тестового изображения
    print("📷 Создание тестового изображения...")
    test_image = create_test_image()
    test_image.save("test_interface_fix_document.png")
    print("✅ Тестовое изображение создано: test_interface_fix_document.png")
    
    # Конвертация в base64
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Официальные промпты
    official_prompts = {
        "🔤 Простое OCR": "Extract all text from this image.",
        "📋 Детальное OCR": "Extract all text content from this image while maintaining reading order. Exclude headers and footers.",
        "🏗️ Анализ структуры": "Extract text, layout, and structure from this document image. Include bounding boxes, categories, and format tables as HTML, formulas as LaTeX, and text as Markdown.",
        "📊 Извлечение таблиц": "Extract and format the table content from this document as structured data.",
        "📄 Структурированное извлечение": "Analyze this document and extract structured information including text, tables, and layout elements."
    }
    
    # Получение лимита модели
    base_url = "http://localhost:8000"
    model_max_tokens = 8192  # Из конфигурации
    
    results = []
    
    print(f"🔍 Тестирование {len(official_prompts)} промптов с безопасными токенами...")
    
    for prompt_name, prompt_text in official_prompts.items():
        print(f"\n   🧪 {prompt_name}")
        
        # Расчет безопасных токенов (как в исправленном коде)
        requested_tokens = 4096  # Стандартное значение из интерфейса
        safe_max_tokens = min(requested_tokens, model_max_tokens - 500)
        
        if safe_max_tokens < 100:
            safe_max_tokens = model_max_tokens // 2
        
        print(f"      🎯 Безопасные токены: {safe_max_tokens} (лимит модели: {model_max_tokens})")
        
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": safe_max_tokens,  # Используем безопасное значение
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
                
                results.append({
                    "prompt_name": prompt_name,
                    "prompt": prompt_text,
                    "success": True,
                    "processing_time": processing_time,
                    "tokens_used": tokens_used,
                    "safe_max_tokens": safe_max_tokens,
                    "response_length": len(content),
                    "response": content
                })
                
                # Показываем первые 150 символов ответа
                preview = content[:150] + "..." if len(content) > 150 else content
                print(f"      📝 Превью: {preview}")
                
            else:
                error_text = response.text
                print(f"      ❌ Ошибка: {response.status_code}")
                print(f"         Ответ: {error_text[:200]}...")
                
                # Проверяем, есть ли ошибка токенов
                if "max_tokens" in error_text and "exceeds" in error_text:
                    print(f"      🚨 ОШИБКА ТОКЕНОВ! Безопасное значение {safe_max_tokens} всё ещё слишком большое")
                
                results.append({
                    "prompt_name": prompt_name,
                    "prompt": prompt_text,
                    "success": False,
                    "error": response.status_code,
                    "error_text": error_text[:200],
                    "safe_max_tokens": safe_max_tokens
                })
                
        except Exception as e:
            print(f"      ❌ Исключение: {e}")
            results.append({
                "prompt_name": prompt_name,
                "prompt": prompt_text,
                "success": False,
                "error": "exception",
                "error_text": str(e),
                "safe_max_tokens": safe_max_tokens
            })
    
    return results

def analyze_fix_results(results):
    """Анализ результатов исправления"""
    
    print("\n" + "=" * 60)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ ИСПРАВЛЕНИЯ")
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
        avg_safe_tokens = sum(r["safe_max_tokens"] for r in successful_tests) / len(successful_tests)
        
        print(f"   ⏱️ Среднее время: {avg_time:.1f}с")
        print(f"   🎯 Средние токены: {avg_tokens:.0f}")
        print(f"   🛡️ Средние безопасные токены: {avg_safe_tokens:.0f}")
    
    # Проверка уникальности ответов
    if len(successful_tests) > 1:
        print(f"\n🔍 АНАЛИЗ УНИКАЛЬНОСТИ ОТВЕТОВ:")
        
        responses = [r["response"] for r in successful_tests]
        unique_responses = set(responses)
        
        print(f"   📊 Всего ответов: {len(responses)}")
        print(f"   🎯 Уникальных ответов: {len(unique_responses)}")
        
        if len(unique_responses) == 1:
            print("   ❌ ВСЕ ОТВЕТЫ ОДИНАКОВЫЕ! Исправление не помогло!")
        elif len(unique_responses) == len(responses):
            print("   ✅ ВСЕ ОТВЕТЫ УНИКАЛЬНЫЕ! Исправление работает!")
        else:
            print(f"   ⚠️ Частично уникальные ответы: {len(unique_responses)}/{len(responses)}")
    
    # Проверка ошибок токенов
    token_errors = [r for r in failed_tests if "max_tokens" in r.get("error_text", "")]
    if token_errors:
        print(f"\n🚨 ОШИБКИ ТОКЕНОВ:")
        print(f"   ❌ Количество ошибок токенов: {len(token_errors)}")
        print("   💡 Необходимо дальнейшее уменьшение безопасных токенов")
    else:
        print(f"\n✅ ТОКЕНЫ:")
        print("   ✅ Нет ошибок валидации токенов!")
        print("   🎯 Безопасный расчет токенов работает корректно")
    
    # Сохранение результатов
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "interface_fix_verification",
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": (len(successful_tests)/len(results)*100) if results else 0,
            "unique_responses": len(set(r["response"] for r in successful_tests)) if successful_tests else 0,
            "token_errors": len(token_errors),
            "fix_status": "SUCCESS" if len(successful_tests) > 0 and len(token_errors) == 0 else "NEEDS_WORK"
        }
    }
    
    with open("official_prompts_interface_fix_test.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Подробный отчет сохранен: official_prompts_interface_fix_test.json")
    
    # Финальная оценка
    print(f"\n🎯 ФИНАЛЬНАЯ ОЦЕНКА ИСПРАВЛЕНИЯ:")
    
    if len(successful_tests) == len(results) and len(token_errors) == 0:
        print("   🎉 ИСПРАВЛЕНИЕ ПОЛНОСТЬЮ УСПЕШНО!")
        print("   ✅ Все официальные промпты работают")
        print("   ✅ Нет ошибок валидации токенов")
        print("   ✅ Система готова к использованию")
    elif len(successful_tests) > 0 and len(token_errors) == 0:
        print("   ✅ ИСПРАВЛЕНИЕ В ОСНОВНОМ УСПЕШНО")
        print(f"   ✅ {len(successful_tests)}/{len(results)} промптов работают")
        print("   ✅ Нет ошибок валидации токенов")
    elif len(token_errors) > 0:
        print("   ⚠️ ИСПРАВЛЕНИЕ ЧАСТИЧНО УСПЕШНО")
        print(f"   ❌ Остались ошибки токенов: {len(token_errors)}")
        print("   💡 Необходимо дальнейшее уменьшение лимитов")
    else:
        print("   ❌ ИСПРАВЛЕНИЕ НЕ ПОМОГЛО")
        print("   🚨 Требуется дополнительная диагностика")

def main():
    """Главная функция"""
    
    print("🔧 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ ОФИЦИАЛЬНЫХ ПРОМПТОВ")
    print("=" * 60)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Тестирование расчета токенов
    if not test_token_calculation():
        return
    
    # Тестирование официальных промптов
    results = test_official_prompts_with_safe_tokens()
    if results:
        analyze_fix_results(results)

if __name__ == "__main__":
    main()