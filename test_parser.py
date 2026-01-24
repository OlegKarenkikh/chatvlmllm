#!/usr/bin/env python3
"""Тест парсера layout элементов"""

import json

# Пример ответа модели (ваш НОВЫЙ реальный ответ)
sample_response = """[{"bbox": [80, 28, 220, 115], "category": "Picture"}, {"bbox": [309, 52, 873, 104], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"}, {"bbox": [333, 129, 575, 181], "category": "List-item", "text": "1. ВАКАРИНЦЕВ\n VAKARINTSEV"}, {"bbox": [331, 184, 665, 237], "category": "List-item", "text": "2. АНДРЕЙ ПАВЛОВИЧ\n ANDREY PAVLOVICH"}, {"bbox": [331, 241, 636, 325], "category": "List-item", "text": "3. 13.09.1995\n АЛТАЙСКИЙ КРАЙ\n ALTAYSKIY KRAY"}, {"bbox": [331, 327, 521, 361], "category": "List-item", "text": "4а) 03.01.2014"}, {"bbox": [332, 361, 544, 413], "category": "List-item", "text": "4с) ГИБДД 2247\nGIBDD 2247"}, {"bbox": [329, 416, 549, 448], "category": "List-item", "text": "5. 22 13 616660"}, {"bbox": [329, 450, 635, 503], "category": "List-item", "text": "8. АЛТАЙСКИЙ КРАЙ\nALTAYSKIY KRAY"}, {"bbox": [329, 518, 417, 559], "category": "List-item", "text": "9. [ ]"}, {"bbox": [46, 148, 284, 489], "category": "Picture"}, {"bbox": [34, 500, 60, 528], "category": "Text", "text": "6."}, {"bbox": [33, 538, 247, 612], "category": "Picture"}]"""

def parse_layout_elements(content: str):
    """Парсинг элементов layout из ответа модели"""
    
    try:
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
                    for key in ['elements', 'layout', 'items', 'results', 'data']:
                        if key in data and isinstance(data[key], list):
                            return data[key]
                    if 'bbox' in data:
                        return [data]
                return []
                
            except json.JSONDecodeError as e:
                # Если ошибка из-за управляющих символов, пробуем исправить
                print(f"⚠️ Ошибка JSON (пытаемся исправить): {e}")
                
                import re
                
                # Заменяем неэкранированные \n на пробелы в значениях text
                def fix_newlines(match):
                    text = match.group(1)
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
        
        return []
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

# Тест
print("🧪 Тестирование парсера layout элементов")
print("=" * 60)

elements = parse_layout_elements(sample_response)

print(f"✅ Найдено элементов: {len(elements)}")
print()

# Статистика по категориям
categories = {}
for elem in elements:
    cat = elem.get('category', 'Unknown')
    categories[cat] = categories.get(cat, 0) + 1

print("📊 Категории:")
for cat, count in sorted(categories.items()):
    print(f"   - {cat}: {count}")

print()
print("📋 Первые 3 элемента:")
for i, elem in enumerate(elements[:3]):
    print(f"\n   {i+1}. {elem.get('category', 'Unknown')}")
    print(f"      bbox: {elem.get('bbox')}")
    if 'text' in elem:
        text = elem['text'][:50] + "..." if len(elem['text']) > 50 else elem['text']
        print(f"      text: {text}")

print("\n" + "=" * 60)
print("✅ ТЕСТ ЗАВЕРШЕН")
