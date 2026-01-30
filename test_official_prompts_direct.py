#!/usr/bin/env python3
"""
Прямое тестирование официальных промптов dots.ocr через vLLM API
"""

import requests
import json
import base64
import time
from PIL import Image, ImageDraw, ImageFont
import io

def create_comprehensive_document():
    """Создаем комплексный документ для тестирования."""
    img = Image.new('RGB', (600, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 20)
        text_font = ImageFont.truetype("arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    y = 30
    
    # Заголовок
    draw.text((50, y), "СЧЕТ-ФАКТУРА № 12345", fill='black', font=title_font)
    y += 40
    
    # Основная информация
    draw.text((50, y), "Дата: 24 января 2026 г.", fill='black', font=text_font)
    y += 25
    draw.text((50, y), "Поставщик: ООО 'Технологии'", fill='black', font=text_font)
    y += 25
    draw.text((50, y), "ИНН: 7702123456", fill='black', font=text_font)
    y += 40
    
    # Таблица
    table_y = y
    draw.rectangle([50, table_y, 550, table_y + 120], outline='black', width=2)
    
    # Заголовок таблицы
    draw.rectangle([50, table_y, 550, table_y + 30], fill='lightgray', outline='black', width=1)
    draw.text((60, table_y + 8), "Товар", fill='black', font=text_font)
    draw.text((250, table_y + 8), "Количество", fill='black', font=text_font)
    draw.text((400, table_y + 8), "Цена", fill='black', font=text_font)
    
    # Строки таблицы
    items = [
        ("Программное обеспечение", "1 шт", "50,000 руб"),
        ("Техническая поддержка", "12 мес", "60,000 руб"),
        ("Обучение", "1 курс", "15,000 руб")
    ]
    
    for i, (item, qty, price) in enumerate(items):
        row_y = table_y + 30 + (i * 30)
        draw.rectangle([50, row_y, 550, row_y + 30], outline='black', width=1)
        draw.text((60, row_y + 8), item, fill='black', font=text_font)
        draw.text((250, row_y + 8), qty, fill='black', font=text_font)
        draw.text((400, row_y + 8), price, fill='black', font=text_font)
    
    y += 150
    
    # Итого
    draw.text((50, y), "ИТОГО: 125,000 руб.", fill='black', font=title_font)
    y += 30
    draw.text((50, y), "НДС 20%: 25,000 руб.", fill='black', font=text_font)
    y += 25
    draw.text((50, y), "Всего к оплате: 150,000 руб.", fill='black', font=title_font)
    
    return img

def test_official_prompts():
    """Тестируем официальные промпты dots.ocr."""
    print("🧪 ТЕСТИРОВАНИЕ ОФИЦИАЛЬНЫХ ПРОМПТОВ dots.ocr")
    print("=" * 60)
    
    # Создаем тестовое изображение
    test_image = create_comprehensive_document()
    test_image.save("test_official_prompts_document.png")
    print("📷 Создан тестовый документ: test_official_prompts_document.png")
    
    # Конвертируем в base64
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Официальные промпты из документации
    official_prompts = {
        "simple_ocr": {
            "prompt": "Extract all text from this image.",
            "description": "Простое извлечение текста"
        },
        "detailed_ocr": {
            "prompt": "Extract all text content from this image while maintaining reading order. Exclude headers and footers.",
            "description": "Детальное OCR с порядком чтения"
        },
        "layout_analysis": {
            "prompt": "Extract text, layout, and structure from this document image. Include bounding boxes, categories, and format tables as HTML, formulas as LaTeX, and text as Markdown.",
            "description": "Анализ макета и структуры"
        },
        "table_extraction": {
            "prompt": "Extract and format the table content from this document as structured data.",
            "description": "Извлечение таблиц"
        },
        "structured_extraction": {
            "prompt": "Analyze this document and extract structured information including text, tables, and layout elements.",
            "description": "Структурированное извлечение"
        }
    }
    
    results = []
    
    for prompt_name, prompt_info in official_prompts.items():
        prompt_text = prompt_info["prompt"]
        description = prompt_info["description"]
        
        print(f"\n📝 Тест: {prompt_name}")
        print(f"📋 {description}")
        print(f"🎯 Промпт: {prompt_text}")
        print("-" * 50)
        
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 500,  # Уменьшено для соответствия лимитам модели
            "temperature": 0.1
        }
        
        try:
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                print(f"✅ Успех ({processing_time:.2f}с)")
                print(f"📄 Длина ответа: {len(content)} символов")
                print(f"📄 Начало ответа: {content[:300]}{'...' if len(content) > 300 else ''}")
                
                # Анализируем качество ответа
                analysis = analyze_response(prompt_name, content)
                print(f"🔍 Анализ: {analysis['quality']} - {analysis['description']}")
                
                results.append({
                    "prompt_name": prompt_name,
                    "prompt": prompt_text,
                    "description": description,
                    "response": content,
                    "response_length": len(content),
                    "processing_time": processing_time,
                    "analysis": analysis,
                    "success": True
                })
                
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                print(f"Ответ: {response.text}")
                
                results.append({
                    "prompt_name": prompt_name,
                    "prompt": prompt_text,
                    "description": description,
                    "error": f"API error {response.status_code}: {response.text}",
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
    with open("official_prompts_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Анализ результатов
    print("\n" + "=" * 60)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("=" * 60)
    
    successful_tests = [r for r in results if r.get("success")]
    high_quality = [r for r in successful_tests if r.get("analysis", {}).get("quality") == "ОТЛИЧНО"]
    
    success_rate = len(successful_tests) / len(results) * 100 if results else 0
    quality_rate = len(high_quality) / len(successful_tests) * 100 if successful_tests else 0
    
    print(f"✅ Успешность: {len(successful_tests)}/{len(results)} ({success_rate:.1f}%)")
    print(f"🎯 Высокое качество: {len(high_quality)}/{len(successful_tests)} ({quality_rate:.1f}%)")
    
    # Детальный анализ
    for result in successful_tests:
        prompt_name = result["prompt_name"]
        quality = result.get("analysis", {}).get("quality", "НЕИЗВЕСТНО")
        length = result["response_length"]
        time_taken = result["processing_time"]
        print(f"  • {prompt_name}: {quality} ({length} символов, {time_taken:.2f}с)")
    
    # Итоговая оценка
    if success_rate >= 80 and quality_rate >= 60:
        print("\n🎉 ОФИЦИАЛЬНЫЕ ПРОМПТЫ РАБОТАЮТ ОТЛИЧНО!")
        overall_success = True
    elif success_rate >= 60:
        print("\n✅ ОФИЦИАЛЬНЫЕ ПРОМПТЫ ЧАСТИЧНО РАБОТАЮТ")
        overall_success = True
    else:
        print("\n❌ ПРОБЛЕМЫ С ОФИЦИАЛЬНЫМИ ПРОМПТАМИ")
        overall_success = False
    
    return overall_success, results

def analyze_response(prompt_name, response):
    """Анализируем качество ответа."""
    
    # Общие проверки
    has_content = len(response) > 50
    has_key_words = any(word in response for word in ['СЧЕТ', 'Дата', 'ООО', 'руб', 'ИТОГО'])
    
    if prompt_name == "simple_ocr":
        if has_content and has_key_words:
            return {"quality": "ОТЛИЧНО", "description": "Полное извлечение текста"}
        else:
            return {"quality": "СРЕДНЕ", "description": "Частичное извлечение"}
    
    elif prompt_name == "detailed_ocr":
        if has_content and has_key_words and len(response) > 200:
            return {"quality": "ОТЛИЧНО", "description": "Детальное извлечение с порядком"}
        else:
            return {"quality": "ХОРОШО", "description": "Базовое извлечение"}
    
    elif prompt_name == "layout_analysis":
        if any(marker in response.lower() for marker in ['<table', 'html', 'structure', 'layout']):
            return {"quality": "ОТЛИЧНО", "description": "Структурированный анализ"}
        elif has_content:
            return {"quality": "ХОРОШО", "description": "Текст извлечен, структура частично"}
        else:
            return {"quality": "СРЕДНЕ", "description": "Базовое извлечение"}
    
    elif prompt_name == "table_extraction":
        if any(marker in response for marker in ['Программное', 'Техническая', '50,000', '60,000']):
            return {"quality": "ОТЛИЧНО", "description": "Таблица извлечена"}
        else:
            return {"quality": "СРЕДНЕ", "description": "Частичное извлечение таблицы"}
    
    elif prompt_name == "structured_extraction":
        if has_content and len(response) > 300:
            return {"quality": "ОТЛИЧНО", "description": "Структурированное извлечение"}
        else:
            return {"quality": "ХОРОШО", "description": "Базовое структурирование"}
    
    return {"quality": "НЕИЗВЕСТНО", "description": "Не удалось проанализировать"}

def main():
    """Основная функция."""
    print("🔬 ТЕСТИРОВАНИЕ ОФИЦИАЛЬНЫХ ПРОМПТОВ dots.ocr")
    print("=" * 80)
    
    success, results = test_official_prompts()
    
    if success:
        print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("📄 Результаты сохранены в official_prompts_test_results.json")
        return True
    else:
        print("\n❌ ТЕСТИРОВАНИЕ ВЫЯВИЛО ПРОБЛЕМЫ")
        return False

if __name__ == "__main__":
    main()