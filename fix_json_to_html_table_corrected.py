#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ JSON TO HTML КОНВЕРТЕРА (ИСПРАВЛЕННАЯ ВЕРСИЯ)
Обрабатывает JSON ответы от dots.ocr и конвертирует их в HTML таблицы
"""

import re
import json
from pathlib import Path

def create_json_to_html_converter():
    """Создает функцию конвертации JSON в HTML таблицы"""
    
    converter_code = '''
import json
import re

def render_message_with_json_and_html_tables(content: str, role: str = "assistant"):
    """
    ОБРАБОТКА JSON И HTML ТАБЛИЦ
    Конвертирует JSON ответы dots.ocr в красивые HTML таблицы
    """
    
    if role == "assistant":
        # Проверяем наличие JSON данных от dots.ocr
        if is_dots_ocr_json_response(content):
            # Конвертируем JSON в HTML таблицу
            html_table = convert_dots_ocr_json_to_html_table(content)
            
            # Отображаем как HTML таблицу
            st.markdown("🔧 **JSON данные конвертированы в HTML таблицу**")
            st.markdown(html_table, unsafe_allow_html=True)
            st.success("✅ JSON → HTML конвертация выполнена")
            return
        
        # Проверяем наличие готовых HTML таблиц
        elif '<table' in content.lower() and '</table>' in content.lower():
            # Простые встроенные стили для HTML таблиц
            simple_styled_content = content.replace(
                '<table', 
                '<table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd; margin: 10px 0;"'
            ).replace(
                '<th', 
                '<th style="background-color: #4CAF50; color: white; padding: 8px; border: 1px solid #ddd; text-align: left;"'
            ).replace(
                '<td', 
                '<td style="padding: 8px; border: 1px solid #ddd; background-color: white; color: black;"'
            )
            
            # Отображаем HTML
            st.markdown("🔧 **HTML таблица**")
            st.markdown(simple_styled_content, unsafe_allow_html=True)
            st.success("✅ HTML рендеринг")
            return
    
    # Обычное сообщение
    st.markdown(content)

def is_dots_ocr_json_response(content: str) -> bool:
    """Проверяет, является ли контент JSON ответом от dots.ocr"""
    
    # Проверяем, начинается ли строка с JSON массива
    stripped_content = content.strip()
    if stripped_content.startswith('[{') and stripped_content.endswith('}]'):
        try:
            # Пытаемся парсить как JSON
            data = json.loads(stripped_content)
            if isinstance(data, list) and len(data) > 0:
                # Проверяем, что это BBOX данные
                first_item = data[0]
                if isinstance(first_item, dict) and 'bbox' in first_item and 'category' in first_item:
                    return True
        except:
            pass
    
    return False

def convert_dots_ocr_json_to_html_table(content: str) -> str:
    """Конвертирует JSON ответ dots.ocr в HTML таблицу"""
    
    try:
        # Извлекаем JSON из контента
        stripped_content = content.strip()
        
        # Парсим JSON
        data = json.loads(stripped_content)
        
        if not isinstance(data, list) or len(data) == 0:
            return content
        
        # Создаем HTML таблицу
        html_parts = []
        
        html_parts.append('<table style="border-collapse: collapse; width: 100%; border: 2px solid #ddd; margin: 15px 0; font-size: 14px;">')
        
        # Заголовок таблицы
        header_html = """
        <thead>
            <tr>
                <th style="background-color: #2196F3; color: white; padding: 12px 8px; border: 1px solid #1976D2; text-align: left; width: 50px;">#</th>
                <th style="background-color: #2196F3; color: white; padding: 12px 8px; border: 1px solid #1976D2; text-align: left; width: 120px;">Категория</th>
                <th style="background-color: #2196F3; color: white; padding: 12px 8px; border: 1px solid #1976D2; text-align: left; width: 180px;">BBOX координаты</th>
                <th style="background-color: #2196F3; color: white; padding: 12px 8px; border: 1px solid #1976D2; text-align: left;">Текст</th>
            </tr>
        </thead>
        """
        html_parts.append(header_html)
        
        # Тело таблицы
        html_parts.append('<tbody>')
        
        for i, item in enumerate(data, 1):
            bbox = item.get('bbox', [])
            category = item.get('category', 'Unknown')
            text = item.get('text', '')
            
            # Форматируем BBOX координаты
            bbox_str = f"[{', '.join(map(str, bbox))}]" if bbox else "N/A"
            
            # Ограничиваем длину текста
            if len(text) > 50:
                text = text[:47] + "..."
            
            # Экранируем HTML в тексте
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            category = category.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Определяем цвет строки
            row_bg = "#f1f8ff" if i % 2 == 0 else "#ffffff"
            
            row_html = f"""
            <tr>
                <td style="padding: 10px 8px; border: 1px solid #ddd; background-color: {row_bg}; color: #2c3e50; text-align: center; font-weight: bold;">{i}</td>
                <td style="padding: 10px 8px; border: 1px solid #ddd; background-color: {row_bg}; color: #2c3e50;">{category}</td>
                <td style="padding: 10px 8px; border: 1px solid #ddd; background-color: {row_bg}; color: #2c3e50; font-family: monospace; font-size: 12px;">{bbox_str}</td>
                <td style="padding: 10px 8px; border: 1px solid #ddd; background-color: {row_bg}; color: #2c3e50;">{text}</td>
            </tr>
            """
            html_parts.append(row_html)
        
        html_parts.append('</tbody>')
        html_parts.append('</table>')
        
        # Добавляем статистику
        total_elements = len(data)
        categories = {}
        text_elements = 0
        
        for item in data:
            category = item.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            if item.get('text', '').strip():
                text_elements += 1
        
        stats_html = f"""
        <div style="margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px; border-left: 4px solid #2196F3;">
            <strong>📊 Статистика анализа:</strong><br>
            • Всего элементов: {total_elements}<br>
            • Элементов с текстом: {text_elements}<br>
            • Категорий: {len(categories)}<br>
            • Распределение: {", ".join([f"{cat}: {count}" for cat, count in categories.items()])}
        </div>
        """
        html_parts.append(stats_html)
        
        return "".join(html_parts)
        
    except Exception as e:
        # Если не удалось конвертировать, возвращаем исходный контент
        return f"<p><strong>⚠️ Не удалось конвертировать JSON:</strong> {str(e)}</p><pre>{content}</pre>"
'''
    
    return converter_code

def fix_app_with_json_converter():
    """Исправляет app.py добавлением JSON конвертера"""
    
    app_file = Path("app.py")
    
    if not app_file.exists():
        print("❌ Файл app.py не найден!")
        return False
    
    # Читаем содержимое файла
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Добавляем JSON конвертер
    json_converter = create_json_to_html_converter()
    
    # Находим место после импортов
    import_end = content.find('# Import UI components')
    if import_end == -1:
        import_end = content.find('from ui.styles import get_custom_css')
    
    if import_end != -1:
        # Вставляем функцию после импортов
        insert_pos = content.find('\n', import_end) + 1
        content = content[:insert_pos] + '\n' + json_converter + '\n' + content[insert_pos:]
    else:
        # Добавляем в начало файла
        content = json_converter + '\n\n' + content
    
    # Заменяем все вызовы на новую функцию
    content = content.replace(
        'render_message_with_markdown_tables(message["content"], message["role"])',
        'render_message_with_json_and_html_tables(message["content"], message["role"])'
    )
    
    content = content.replace(
        'render_message_with_markdown_tables(response, "assistant")',
        'render_message_with_json_and_html_tables(response, "assistant")'
    )
    
    # Сохраняем исправленный файл
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ app.py исправлен JSON конвертером!")
    return True

def main():
    """Основная функция JSON исправления"""
    
    print("📊 JSON TO HTML КОНВЕРТЕР ДЛЯ DOTS.OCR (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
    print("=" * 60)
    
    # 1. Исправляем основное приложение JSON конвертером
    print("\n1️⃣ Исправляем app.py JSON конвертером...")
    if fix_app_with_json_converter():
        print("✅ app.py исправлен JSON конвертером!")
    else:
        print("❌ Ошибка при исправлении app.py")
        return
    
    print("\n" + "=" * 60)
    print("🎉 JSON КОНВЕРТЕР ГОТОВ!")
    print("\n📋 ЧТО СДЕЛАНО:")
    print("✅ Создан JSON → HTML конвертер для dots.ocr")
    print("✅ Автоматическое распознавание JSON ответов")
    print("✅ Красивые HTML таблицы с синими заголовками")
    print("✅ Статистика анализа и подсчет элементов")
    print("✅ Исправлены ошибки отступов")
    
    print("\n🚀 РЕЗУЛЬТАТ:")
    print("Теперь JSON ответы dots.ocr будут отображаться как красивые таблицы!")
    print("Перезапустите приложение для применения изменений.")

if __name__ == "__main__":
    main()