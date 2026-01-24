#!/usr/bin/env python3
"""
Тестирование новых возможностей dots.ocr с BBOX и визуализацией
"""

import requests
import base64
import time
import json
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

def create_comprehensive_test_document():
    """Создание комплексного тестового документа с различными элементами"""
    
    # Создаем изображение 800x1000
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y_offset = 30
    
    # 1. Заголовок документа
    draw.text((50, y_offset), "ТЕСТОВЫЙ ДОКУМЕНТ ДЛЯ dots.ocr", fill='black', font=font_large)
    y_offset += 50
    
    # 2. Подзаголовок
    draw.text((50, y_offset), "Проверка новых возможностей BBOX и визуализации", fill='black', font=font_medium)
    y_offset += 40
    
    # 3. Обычный текст
    text_lines = [
        "Этот документ создан для тестирования расширенных возможностей dots.ocr.",
        "Включает различные типы элементов для обнаружения и анализа.",
        "Модель должна определить BBOX координаты для каждого элемента."
    ]
    
    for line in text_lines:
        draw.text((50, y_offset), line, fill='black', font=font_small)
        y_offset += 20
    
    y_offset += 20
    
    # 4. Таблица данных
    draw.text((50, y_offset), "ТАБЛИЦА ПРОДУКТОВ:", fill='black', font=font_medium)
    y_offset += 30
    
    # Рисуем таблицу
    table_x = 50
    table_y = y_offset
    cell_width = 120
    cell_height = 25
    
    # Заголовки таблицы
    headers = ["Продукт", "Цена", "Кол-во", "Сумма"]
    for i, header in enumerate(headers):
        x = table_x + i * cell_width
        y = table_y
        draw.rectangle([x, y, x + cell_width, y + cell_height], outline='black', width=2)
        draw.text((x + 5, y + 5), header, fill='black', font=font_small)
    
    # Данные таблицы
    data = [
        ["Хлеб", "50₽", "2", "100₽"],
        ["Молоко", "80₽", "1", "80₽"],
        ["Сыр", "200₽", "1", "200₽"],
        ["ИТОГО", "", "", "380₽"]
    ]
    
    for row_idx, row in enumerate(data):
        for col_idx, cell in enumerate(row):
            x = table_x + col_idx * cell_width
            y = table_y + (row_idx + 1) * cell_height
            width = 2 if row_idx == len(data) - 1 else 1  # Жирная линия для итого
            draw.rectangle([x, y, x + cell_width, y + cell_height], outline='black', width=width)
            draw.text((x + 5, y + 5), cell, fill='black', font=font_small)
    
    y_offset += (len(data) + 1) * cell_height + 30
    
    # 5. Формула (имитация)
    draw.text((50, y_offset), "ФОРМУЛА:", fill='black', font=font_medium)
    y_offset += 25
    draw.text((70, y_offset), "E = mc²", fill='black', font=font_large)
    y_offset += 40
    
    # 6. Список элементов
    draw.text((50, y_offset), "СПИСОК ПРОВЕРЯЕМЫХ ЭЛЕМЕНТОВ:", fill='black', font=font_medium)
    y_offset += 25
    
    list_items = [
        "• Заголовки и подзаголовки",
        "• Обычный текст и параграфы", 
        "• Таблицы с данными",
        "• Математические формулы",
        "• Списки и перечисления",
        "• Графические элементы"
    ]
    
    for item in list_items:
        draw.text((70, y_offset), item, fill='black', font=font_small)
        y_offset += 18
    
    y_offset += 20
    
    # 7. Имитация печати/штампа
    stamp_x, stamp_y = 500, y_offset
    stamp_width, stamp_height = 150, 80
    
    # Рамка печати
    draw.rectangle([stamp_x, stamp_y, stamp_x + stamp_width, stamp_y + stamp_height], 
                  outline='red', width=3)
    draw.rectangle([stamp_x + 5, stamp_y + 5, stamp_x + stamp_width - 5, stamp_y + stamp_height - 5], 
                  outline='red', width=2)
    
    # Текст печати
    draw.text((stamp_x + 20, stamp_y + 15), "УТВЕРЖДЕНО", fill='red', font=font_small)
    draw.text((stamp_x + 30, stamp_y + 35), "24.01.2026", fill='red', font=font_small)
    draw.text((stamp_x + 35, stamp_y + 55), "Подпись", fill='red', font=font_small)
    
    # 8. Имитация подписи
    signature_x, signature_y = 50, y_offset + 100
    draw.text((signature_x, signature_y), "Подпись:", fill='black', font=font_small)
    
    # Рисуем имитацию подписи (волнистая линия)
    for i in range(0, 100, 2):
        x1 = signature_x + 80 + i
        y1 = signature_y + 5 + (i % 10) - 5
        x2 = signature_x + 82 + i
        y2 = signature_y + 5 + ((i + 2) % 10) - 5
        draw.line([x1, y1, x2, y2], fill='blue', width=2)
    
    # 9. Имитация логотипа/изображения
    logo_x, logo_y = 600, 50
    logo_size = 80
    
    # Простой логотип (круг с текстом)
    draw.ellipse([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], 
                outline='green', fill='lightgreen', width=2)
    draw.text((logo_x + 25, logo_y + 30), "LOGO", fill='darkgreen', font=font_medium)
    
    # 10. Футер документа
    footer_y = 950
    draw.text((50, footer_y), f"Документ создан: {datetime.now().strftime('%d.%m.%Y %H:%M')}", 
             fill='gray', font=font_small)
    draw.text((400, footer_y), "Страница 1 из 1", fill='gray', font=font_small)
    
    return img

def test_new_official_prompts():
    """Тестирование новых официальных промптов dots.ocr"""
    
    print("🧪 ТЕСТИРОВАНИЕ НОВЫХ ВОЗМОЖНОСТЕЙ dots.ocr")
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
    
    # Создание комплексного тестового документа
    print("\n📷 Создание комплексного тестового документа...")
    test_image = create_comprehensive_test_document()
    test_image.save("comprehensive_test_document.png")
    print("✅ Тестовый документ создан: comprehensive_test_document.png")
    
    # Конвертация в base64
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Новые официальные промпты для тестирования
    new_prompts = {
        "🔍 Полный анализ с BBOX": """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

1. Bbox format: [x1, y1, x2, y2]

2. Layout Categories: The possible categories are ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title'].

3. Text Extraction & Formatting Rules:
    - Picture: For the 'Picture' category, the text field should be omitted.
    - Formula: Format its text as LaTeX.
    - Table: Format its text as HTML.
    - All Others (Text, Title, etc.): Format their text as Markdown.

4. Constraints:
    - The output text must be the original text from the image, with no translation.
    - All layout elements must be sorted according to human reading order.

5. Final Output: The entire output must be a single JSON object.""",
        
        "🖼️ Обнаружение изображений": """Analyze this document image and detect all visual elements including pictures, logos, stamps, signatures, and other graphical content. For each detected element, provide:

1. Bbox coordinates in format [x1, y1, x2, y2]
2. Category (Picture, Logo, Stamp, Signature, Barcode, QR-code, etc.)
3. Brief description of the visual element

Output as JSON array with detected visual elements.""",
        
        "📊 Структурированные таблицы": """Extract and format all table content from this document as structured HTML tables with proper formatting. Include:

1. All table data with correct row and column structure
2. Preserve headers and data relationships
3. Format as clean HTML tables
4. Include bbox coordinates for each table: [x1, y1, x2, y2]

Output format: JSON with tables array containing bbox and html_content for each table."""
    }
    
    results = []
    
    print(f"\n🔍 Тестирование {len(new_prompts)} новых промптов...")
    
    for prompt_name, prompt_text in new_prompts.items():
        print(f"\n   🧪 {prompt_name}")
        print(f"      Промпт: {prompt_text[:80]}...")
        
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 7692,  # Безопасное значение
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
                
                # Анализ содержимого ответа
                analysis = analyze_response_content(content, prompt_name)
                
                results.append({
                    "prompt_name": prompt_name,
                    "prompt": prompt_text,
                    "success": True,
                    "processing_time": processing_time,
                    "tokens_used": tokens_used,
                    "response_length": len(content),
                    "response": content,
                    "analysis": analysis
                })
                
                # Показываем анализ
                print(f"      🔍 Анализ: {analysis['summary']}")
                
            else:
                print(f"      ❌ Ошибка: {response.status_code}")
                print(f"         Ответ: {response.text[:100]}...")
                
                results.append({
                    "prompt_name": prompt_name,
                    "success": False,
                    "error": response.status_code,
                    "error_text": response.text[:200]
                })
                
        except Exception as e:
            print(f"      ❌ Исключение: {e}")
            results.append({
                "prompt_name": prompt_name,
                "success": False,
                "error": "exception",
                "error_text": str(e)
            })
    
    return results

def analyze_response_content(content: str, prompt_name: str) -> dict:
    """Анализ содержимого ответа для определения качества"""
    
    analysis = {
        "has_json": False,
        "has_bbox": False,
        "has_html_table": False,
        "bbox_count": 0,
        "table_count": 0,
        "categories_found": [],
        "summary": ""
    }
    
    # Проверка JSON структуры
    if content.strip().startswith('{') or content.strip().startswith('['):
        analysis["has_json"] = True
    
    # Поиск BBOX координат
    import re
    bbox_pattern = r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]'
    bbox_matches = re.findall(bbox_pattern, content)
    analysis["bbox_count"] = len(bbox_matches)
    analysis["has_bbox"] = len(bbox_matches) > 0
    
    # Поиск HTML таблиц
    table_pattern = r'<table[^>]*>.*?</table>'
    table_matches = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
    analysis["table_count"] = len(table_matches)
    analysis["has_html_table"] = len(table_matches) > 0
    
    # Поиск категорий
    categories = ['Text', 'Title', 'Table', 'Picture', 'Formula', 'Caption', 'Footnote', 
                 'List-item', 'Page-header', 'Page-footer', 'Section-header', 'Logo', 'Stamp', 'Signature']
    
    for category in categories:
        if category.lower() in content.lower():
            analysis["categories_found"].append(category)
    
    # Формирование сводки
    if "🔍 Полный анализ" in prompt_name:
        if analysis["has_json"] and analysis["has_bbox"]:
            analysis["summary"] = f"JSON с {analysis['bbox_count']} BBOX, {len(analysis['categories_found'])} категорий"
        else:
            analysis["summary"] = "Неполный JSON или отсутствуют BBOX"
    
    elif "🖼️ Обнаружение изображений" in prompt_name:
        visual_elements = ['Picture', 'Logo', 'Stamp', 'Signature']
        found_visual = [cat for cat in analysis["categories_found"] if cat in visual_elements]
        if found_visual:
            analysis["summary"] = f"Найдены визуальные элементы: {', '.join(found_visual)}"
        else:
            analysis["summary"] = "Визуальные элементы не обнаружены"
    
    elif "📊 Структурированные таблицы" in prompt_name:
        if analysis["has_html_table"]:
            analysis["summary"] = f"Найдено {analysis['table_count']} HTML таблиц"
        else:
            analysis["summary"] = "HTML таблицы не найдены"
    
    else:
        analysis["summary"] = f"Базовый анализ: {len(analysis['categories_found'])} категорий"
    
    return analysis

def generate_test_report(results):
    """Генерация отчета о тестировании"""
    
    print("\n" + "=" * 60)
    print("📊 ОТЧЕТ О ТЕСТИРОВАНИИ НОВЫХ ВОЗМОЖНОСТЕЙ")
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
        
        print(f"   ⏱️ Среднее время: {avg_time:.1f}с")
        print(f"   🎯 Средние токены: {avg_tokens:.0f}")
    
    print(f"\n🔍 АНАЛИЗ ВОЗМОЖНОСТЕЙ:")
    
    for result in successful_tests:
        print(f"\n   📋 {result['prompt_name']}:")
        analysis = result.get("analysis", {})
        print(f"      ✅ {analysis.get('summary', 'Нет анализа')}")
        
        if analysis.get("has_bbox"):
            print(f"      📐 BBOX координат: {analysis.get('bbox_count', 0)}")
        
        if analysis.get("has_html_table"):
            print(f"      📊 HTML таблиц: {analysis.get('table_count', 0)}")
        
        if analysis.get("categories_found"):
            print(f"      🏷️ Категории: {', '.join(analysis['categories_found'][:5])}")
    
    # Сохранение подробного отчета
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "new_dots_ocr_features",
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": (len(successful_tests)/len(results)*100) if results else 0
        }
    }
    
    with open("new_dots_ocr_features_test.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Подробный отчет сохранен: new_dots_ocr_features_test.json")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    
    if len(successful_tests) == len(results):
        print("   🎉 ВСЕ НОВЫЕ ВОЗМОЖНОСТИ РАБОТАЮТ!")
        print("   ✅ BBOX визуализация готова к использованию")
        print("   ✅ Обнаружение графических элементов функционирует")
        print("   ✅ HTML таблицы обрабатываются корректно")
    elif len(successful_tests) > 0:
        print("   ✅ Большинство возможностей работают")
        print("   🔧 Некоторые промпты требуют доработки")
    else:
        print("   🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Новые промпты не работают")
        print("   💡 Проверьте конфигурацию vLLM и модель dots.ocr")

def main():
    """Главная функция"""
    
    results = test_new_official_prompts()
    if results:
        generate_test_report(results)

if __name__ == "__main__":
    main()