#!/usr/bin/env python3
"""
Quick Layout Detection - Обнаружение структуры документа с BBOX координатами
"""

import requests
import base64
import json
import sys
from PIL import Image
import io
from datetime import datetime

def perform_layout_detection(image_path: str):
    """Выполнение layout detection на изображении"""
    
    print("🔍 LAYOUT DETECTION - Обнаружение структуры документа")
    print("=" * 60)
    
    # Проверка vLLM сервера
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ vLLM сервер недоступен. Запустите сервер командой:")
            print("   docker-compose -f docker-compose-vllm.yml up -d")
            return None
        print("✅ vLLM сервер работает")
    except Exception as e:
        print(f"❌ Ошибка подключения к vLLM: {e}")
        print("💡 Запустите сервер: docker-compose -f docker-compose-vllm.yml up -d")
        return None
    
    # Загрузка изображения
    try:
        image = Image.open(image_path)
        print(f"✅ Изображение загружено: {image.size[0]}x{image.size[1]}")
    except Exception as e:
        print(f"❌ Ошибка загрузки изображения: {e}")
        return None
    
    # Конвертация в base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Официальный промпт dots.ocr для layout detection с детальным анализом
    layout_prompt = """Please analyze this document image and detect ALL individual layout elements with precise bounding boxes.

IMPORTANT: Detect EACH separate text field, picture, and element individually. Do not group multiple elements together.

For EACH individual element provide:
1. Bbox coordinates: [x1, y1, x2, y2] - exact pixel coordinates
2. Category from: ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title']
3. Text content if visible (optional)

Rules:
- Detect EVERY text field separately (each line, each label, each value)
- Detect EVERY picture/photo separately
- Detect stamps, signatures, logos as separate Picture elements
- Each numbered item (1., 2., 3., etc.) should be a separate List-item
- Headers should be Section-header category
- Regular text fields should be Text category

Output format: JSON array with ALL detected elements.

Example output structure:
[
  {"bbox": [x1, y1, x2, y2], "category": "Picture", "text": ""},
  {"bbox": [x1, y1, x2, y2], "category": "Section-header", "text": "HEADER TEXT"},
  {"bbox": [x1, y1, x2, y2], "category": "List-item", "text": "1. FIELD NAME"},
  ...
]"""
    
    print(f"\n📤 Отправка запроса к dots.ocr...")
    print(f"   Промпт: Layout Detection (только структура)")
    
    payload = {
        "model": "rednote-hilab/dots.ocr",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": layout_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        }],
        "max_tokens": 7692,
        "temperature": 0.1
    }
    
    try:
        import time
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
            
            print(f"✅ Обработка завершена за {processing_time:.2f}с")
            print(f"🎯 Использовано токенов: {tokens_used}")
            print(f"📄 Длина ответа: {len(content)} символов")
            
            # Показываем начало ответа для отладки
            print(f"\n📋 Начало ответа модели:")
            print(content[:300] + "..." if len(content) > 300 else content)
            print()
            
            # Парсинг результатов
            elements = parse_layout_elements(content)
            
            if elements:
                print(f"\n✅ Обнаружено элементов: {len(elements)}")
                
                # Статистика по категориям
                categories = {}
                for elem in elements:
                    cat = elem.get('category', 'Unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                
                print(f"📊 Категории элементов:")
                for cat, count in sorted(categories.items()):
                    print(f"   - {cat}: {count}")
                
                # Вывод JSON результата
                print(f"\n📋 JSON результат:")
                print(json.dumps(elements, indent=2, ensure_ascii=False))
                
                # Сохранение результата
                output_file = f"layout_detection_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "image": image_path,
                        "image_size": {"width": image.size[0], "height": image.size[1]},
                        "processing_time": processing_time,
                        "tokens_used": tokens_used,
                        "elements_count": len(elements),
                        "categories": categories,
                        "elements": elements
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"\n💾 Результат сохранен: {output_file}")
                
                # Визуализация (если доступна)
                try:
                    from utils.bbox_visualizer import BBoxVisualizer
                    
                    visualizer = BBoxVisualizer()
                    img_with_boxes, legend_img, _ = visualizer.process_dots_ocr_response(
                        image, content, show_labels=True, create_legend_img=True
                    )
                    
                    # Сохранение визуализации
                    viz_file = f"layout_detection_viz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    img_with_boxes.save(viz_file)
                    print(f"🎨 Визуализация сохранена: {viz_file}")
                    
                    if legend_img:
                        legend_file = f"layout_detection_legend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        legend_img.save(legend_file)
                        print(f"📊 Легенда сохранена: {legend_file}")
                    
                except ImportError:
                    print("⚠️ Визуализация недоступна (utils.bbox_visualizer не найден)")
                
                return elements
            else:
                print("⚠️ Элементы не обнаружены в ответе")
                print(f"📄 Ответ модели:\n{content[:500]}...")
                return None
            
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Исключение при обработке: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_layout_elements(content: str):
    """Парсинг элементов layout из ответа модели"""
    
    try:
        # Попытка парсинга как JSON
        content_stripped = content.strip()
        
        # Удаление markdown code blocks если есть
        if content_stripped.startswith('```json'):
            lines = content_stripped.split('\n')
            content_stripped = '\n'.join(lines[1:-1]) if len(lines) > 2 else content_stripped
        elif content_stripped.startswith('```'):
            lines = content_stripped.split('\n')
            content_stripped = '\n'.join(lines[1:-1]) if len(lines) > 2 else content_stripped
        
        # Парсинг JSON с обработкой управляющих символов
        if content_stripped.startswith('[') or content_stripped.startswith('{'):
            try:
                # Прямой парсинг
                data = json.loads(content_stripped)
                
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Поиск массива элементов в объекте
                    for key in ['elements', 'layout', 'items', 'results', 'data']:
                        if key in data and isinstance(data[key], list):
                            return data[key]
                    # Если это единственный элемент
                    if 'bbox' in data:
                        return [data]
                return []
                
            except json.JSONDecodeError as e:
                # Если ошибка из-за управляющих символов, пробуем исправить
                print(f"⚠️ Ошибка JSON (пытаемся исправить): {e}")
                
                # Попытка исправления: заменяем неэкранированные \n на \\n
                import re
                
                # Ищем строки с неэкранированными переносами
                # Паттерн: "text": "что-то\nчто-то"
                def fix_newlines(match):
                    text = match.group(1)
                    # Заменяем \n на пробел для упрощения
                    text = text.replace('\n', ' ')
                    return f'"text": "{text}"'
                
                fixed_content = re.sub(r'"text"\s*:\s*"([^"]*)"', fix_newlines, content_stripped)
                
                try:
                    data = json.loads(fixed_content)
                    if isinstance(data, list):
                        print(f"✅ JSON исправлен, найдено {len(data)} элементов")
                        return data
                    elif isinstance(data, dict) and 'bbox' in data:
                        return [data]
                except:
                    pass
        
        # Если не JSON, попытка извлечения из текста
        import re
        elements = []
        
        # Более агрессивный поиск JSON объектов с bbox
        json_pattern = r'\{[^{}]*?"bbox"\s*:\s*\[[^\]]+\][^{}]*?\}'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        print(f"🔍 Найдено {len(matches)} потенциальных JSON объектов с bbox")
        
        for i, match in enumerate(matches):
            try:
                # Исправляем переносы строк перед парсингом
                fixed_match = match.replace('\n', ' ')
                elem = json.loads(fixed_match)
                if 'bbox' in elem:
                    elements.append(elem)
                    print(f"   ✅ Элемент {i+1}: {elem.get('category', 'Unknown')}")
            except Exception as e:
                print(f"   ⚠️ Элемент {i+1}: ошибка парсинга - {e}")
                continue
        
        if elements:
            return elements
        
        # Последняя попытка - поиск массива в тексте
        array_pattern = r'\[[\s\S]*?\{[\s\S]*?"bbox"[\s\S]*?\}[\s\S]*?\]'
        array_matches = re.findall(array_pattern, content)
        
        if array_matches:
            print(f"🔍 Найден массив элементов, попытка парсинга...")
            try:
                # Исправляем переносы строк
                fixed_array = array_matches[0].replace('\n', ' ')
                return json.loads(fixed_array)
            except:
                pass
        
        return []
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Ошибка парсинга JSON: {e}")
        print(f"📄 Первые 500 символов ответа:\n{content[:500]}")
        return []
    except Exception as e:
        print(f"⚠️ Ошибка обработки ответа: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Главная функция"""
    
    if len(sys.argv) < 2:
        print("📖 Использование:")
        print(f"   python {sys.argv[0]} <путь_к_изображению>")
        print()
        print("📝 Примеры:")
        print(f"   python {sys.argv[0]} test_document.png")
        print(f"   python {sys.argv[0]} examples/passports/passport_sample.jpg")
        print()
        print("💡 Доступные тестовые изображения:")
        import os
        test_images = [f for f in os.listdir('.') if f.endswith(('.png', '.jpg', '.jpeg')) and 'test' in f.lower()]
        for img in test_images[:5]:
            print(f"   - {img}")
        return
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ Файл не найден: {image_path}")
        return
    
    elements = perform_layout_detection(image_path)
    
    if elements:
        print("\n" + "=" * 60)
        print("✅ LAYOUT DETECTION ЗАВЕРШЕН УСПЕШНО")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ LAYOUT DETECTION НЕ УДАЛСЯ")
        print("=" * 60)

if __name__ == "__main__":
    import os
    main()
