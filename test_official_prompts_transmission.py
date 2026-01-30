#!/usr/bin/env python3
"""
Тест передачи официальных промптов dots.ocr
Проверяем, что официальные промпты корректно передаются в vLLM API
"""

import requests
import base64
import json
import time
import subprocess
from PIL import Image, ImageDraw, ImageFont
import io

def create_complex_test_document():
    """Создаем сложный тестовый документ с различными элементами"""
    print("🖼️ Создаем сложный тестовый документ...")
    
    # Создаем изображение большего размера
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "ТЕСТОВЫЙ ДОКУМЕНТ", fill='black', font=font_large)
    
    # Основной текст
    draw.text((50, 100), "Это тестовый документ для проверки", fill='black', font=font_medium)
    draw.text((50, 140), "официальных промптов dots.ocr", fill='black', font=font_medium)
    
    # Таблица (имитация)
    draw.rectangle([50, 200, 400, 350], outline='black', width=2)
    draw.line([50, 230, 400, 230], fill='black', width=1)
    draw.line([200, 200, 200, 350], fill='black', width=1)
    
    draw.text((60, 210), "Название", fill='black', font=font_small)
    draw.text((210, 210), "Значение", fill='black', font=font_small)
    draw.text((60, 250), "Тест 1", fill='black', font=font_small)
    draw.text((210, 250), "123", fill='black', font=font_small)
    draw.text((60, 280), "Тест 2", fill='black', font=font_small)
    draw.text((210, 280), "456", fill='black', font=font_small)
    
    # Формула (имитация)
    draw.text((50, 400), "Формула: E = mc²", fill='black', font=font_medium)
    
    # Список
    draw.text((50, 450), "• Пункт 1", fill='black', font=font_small)
    draw.text((50, 480), "• Пункт 2", fill='black', font=font_small)
    draw.text((50, 510), "• Пункт 3", fill='black', font=font_small)
    
    # Номер страницы (footer)
    draw.text((700, 550), "Стр. 1", fill='gray', font=font_small)
    
    return img

def image_to_base64(image):
    """Конвертируем изображение в base64"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def test_official_prompt(prompt_name, prompt_text, image_base64, expected_features=None):
    """Тест конкретного официального промпта"""
    print(f"\n🎯 Тестируем официальный промпт: {prompt_name}")
    print(f"📝 Промпт: {prompt_text[:100]}...")
    
    url = "http://localhost:8000/v1/chat/completions"
    
    payload = {
        "model": "rednote-hilab/dots.ocr",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.1
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
        processing_time = time.time() - start_time
        
        print(f"⏱️ Время обработки: {processing_time:.2f}с")
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            print(f"✅ Успешный ответ ({len(content)} символов)")
            print(f"📄 Начало ответа: {content[:200]}...")
            
            # Проверяем ожидаемые особенности ответа
            if expected_features:
                found_features = []
                for feature in expected_features:
                    if feature.lower() in content.lower():
                        found_features.append(feature)
                
                if found_features:
                    print(f"✅ Найдены ожидаемые элементы: {', '.join(found_features)}")
                else:
                    print(f"⚠️ Не найдены ожидаемые элементы: {', '.join(expected_features)}")
            
            # Проверяем формат ответа
            if prompt_name == "Полный анализ с BBOX":
                if "bbox" in content.lower() and ("[" in content and "]" in content):
                    print("✅ Обнаружены BBOX координаты")
                else:
                    print("⚠️ BBOX координаты не найдены")
                
                if content.strip().startswith("{") and content.strip().endswith("}"):
                    print("✅ Ответ в формате JSON")
                else:
                    print("⚠️ Ответ не в формате JSON")
            
            elif prompt_name == "Структурированные таблицы":
                if "<table" in content.lower() or "<html" in content.lower():
                    print("✅ Обнаружен HTML формат таблиц")
                else:
                    print("⚠️ HTML таблицы не найдены")
            
            return True, content
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False, response.text
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса (120 сек)")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False, str(e)

def monitor_logs_during_test():
    """Мониторинг логов во время тестирования"""
    print("📋 Мониторим логи контейнера...")
    
    try:
        result = subprocess.run(
            ["docker", "logs", "dots-ocr-fixed", "--tail", "5"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[-3:]:  # Показываем последние 3 строки
                if line.strip():
                    print(f"📋 {line}")
        
    except Exception as e:
        print(f"⚠️ Не удалось получить логи: {e}")

def main():
    """Основная функция тестирования официальных промптов"""
    print("🚀 Тестирование официальных промптов dots.ocr")
    print("=" * 70)
    
    # Создаем тестовое изображение
    test_image = create_complex_test_document()
    image_base64 = image_to_base64(test_image)
    
    # Сохраняем тестовое изображение для визуального контроля
    test_image.save("test_official_prompts_document.png")
    print("💾 Тестовое изображение сохранено как test_official_prompts_document.png")
    
    # Официальные промпты из приложения
    official_prompts = {
        "Полный анализ с BBOX": {
            "prompt": """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

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
            "expected": ["bbox", "json", "layout", "categories"]
        },
        
        "Обнаружение изображений": {
            "prompt": """Analyze this document image and detect all visual elements including pictures, logos, stamps, signatures, and other graphical content. For each detected element, provide:

1. Bbox coordinates in format [x1, y1, x2, y2]
2. Category (Picture, Logo, Stamp, Signature, Barcode, QR-code, etc.)
3. Brief description of the visual element

Output as JSON array with detected visual elements.""",
            "expected": ["bbox", "visual", "elements", "json"]
        },
        
        "Структурированные таблицы": {
            "prompt": """Extract and format all table content from this document as structured HTML tables with proper formatting. Include:

1. All table data with correct row and column structure
2. Preserve headers and data relationships
3. Format as clean HTML tables
4. Include bbox coordinates for each table: [x1, y1, x2, y2]

Output format: JSON with tables array containing bbox and html_content for each table.""",
            "expected": ["table", "html", "bbox", "json"]
        },
        
        "Только обнаружение (BBOX)": {
            "prompt": """Perform layout detection only. Identify and locate all layout elements in the document without text recognition. For each element provide:

1. Bbox coordinates: [x1, y1, x2, y2]
2. Category from: ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title']
3. Confidence score if available

Output as JSON array of detected layout elements.""",
            "expected": ["bbox", "layout", "detection", "json"]
        },
        
        "Простое OCR": {
            "prompt": "Extract all text from this image.",
            "expected": ["тестовый", "документ", "формула"]
        },
        
        "Чтение по порядку": {
            "prompt": "Extract all text content from this image while maintaining reading order. Exclude headers and footers.",
            "expected": ["тестовый", "документ", "пункт"]
        }
    }
    
    # Тестируем каждый официальный промпт
    results = {}
    
    for prompt_name, prompt_info in official_prompts.items():
        print("\n" + "=" * 70)
        
        # Мониторим логи перед запросом
        monitor_logs_during_test()
        
        # Выполняем тест
        success, response = test_official_prompt(
            prompt_name, 
            prompt_info["prompt"], 
            image_base64, 
            prompt_info.get("expected")
        )
        
        results[prompt_name] = {
            "success": success,
            "response_length": len(response) if response else 0,
            "response_preview": response[:300] if response else ""
        }
        
        # Небольшая пауза между запросами
        time.sleep(2)
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ ОФИЦИАЛЬНЫХ ПРОМПТОВ:")
    print("=" * 70)
    
    successful_tests = 0
    total_tests = len(results)
    
    for prompt_name, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"{status} {prompt_name}: {result['response_length']} символов")
        if result["success"]:
            successful_tests += 1
    
    print(f"\n📈 Успешно: {successful_tests}/{total_tests} тестов")
    
    if successful_tests == total_tests:
        print("🎉 Все официальные промпты работают корректно!")
    elif successful_tests > 0:
        print("⚠️ Некоторые официальные промпты работают с проблемами")
    else:
        print("❌ Официальные промпты не работают")
    
    # Финальная проверка логов
    print("\n📋 Финальные логи контейнера:")
    monitor_logs_during_test()

if __name__ == "__main__":
    main()