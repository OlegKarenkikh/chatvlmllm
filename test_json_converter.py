#!/usr/bin/env python3
"""
ТЕСТ JSON КОНВЕРТЕРА
Запуск: streamlit run test_json_converter.py --server.port 8515
"""

import streamlit as st
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

# Настройка страницы
st.set_page_config(
    page_title="JSON Converter Test",
    page_icon="📊",
    layout="wide"
)

# Заголовок
st.title("📊 Тест JSON → HTML конвертера")
st.markdown("**Конвертация JSON ответов dots.ocr в красивые HTML таблицы**")

# Тестовый JSON контент (точно такой же как в чате)
test_json = '''[{"bbox": [189, 85, 234, 104], "category": "Text", "text": "RUS"}, {"bbox": [149, 134, 294, 323], "category": "Picture"}, {"bbox": [162, 343, 175, 358], "category": "Text", "text": "6."}, {"bbox": [161, 356, 175, 370], "category": "Text", "text": "7."}, {"bbox": [310, 84, 637, 115], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"}, {"bbox": [332, 121, 452, 150], "category": "List-item", "text": "1. ИВАНОВ\\n IVANOV"}, {"bbox": [332, 154, 436, 183], "category": "List-item", "text": "2. СЕРГЕЙ\\nSERGEY"}, {"bbox": [332, 187, 643, 232], "category": "List-item", "text": "3. 22.05.1955\\n ТУВИНСКАЯ АВТ. ОБЛ.\\n TUVINSKAYA AVTONOMNAYA OBLAST'"}, {"bbox": [331, 234, 462, 251], "category": "List-item", "text": "4а) 01.02.2020"}, {"bbox": [490, 234, 621, 251], "category": "List-item", "text": "4b) 01.02.2030"}, {"bbox": [331, 254, 469, 283], "category": "List-item", "text": "4с) ГИБДД 7701\\nGIBDD 7701"}, {"bbox": [331, 287, 476, 303], "category": "List-item", "text": "5. 77 07 123456"}, {"bbox": [331, 306, 460, 335], "category": "List-item", "text": "8. Г. МОСКВА\\nG. MOSKVA"}, {"bbox": [331, 338, 436, 357], "category": "Picture"}]'''

# Инициализация сообщений
if "json_test_messages" not in st.session_state:
    st.session_state.json_test_messages = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("🧪 Тестирование JSON конвертера")
    
    if st.button("➕ Добавить JSON ответ dots.ocr", use_container_width=True):
        st.session_state.json_test_messages.append({
            "role": "assistant",
            "content": test_json
        })
        st.rerun()
    
    if st.button("🗑️ Очистить", use_container_width=True):
        st.session_state.json_test_messages = []
        st.rerun()
    
    st.divider()
    
    st.markdown("### 🎯 Что должно произойти:")
    st.markdown("""
    **✅ Ожидаемый результат:**
    - Сообщение "JSON данные конвертированы в HTML таблицу"
    - Красивая таблица с синими заголовками
    - 14 строк с BBOX координатами, категориями и текстом
    - Статистика анализа внизу (14 элементов, 12 с текстом)
    - Сообщение "JSON → HTML конвертация выполнена"
    
    **❌ Если не работает:**
    - Видите сырой JSON код
    - Нет таблицы
    - Нет сообщений подтверждения
    """)

with col2:
    st.subheader("📊 Результат")
    
    if st.session_state.json_test_messages:
        for i, message in enumerate(st.session_state.json_test_messages):
            st.markdown(f"**Тест #{i+1}:**")
            with st.chat_message(message["role"]):
                render_message_with_json_and_html_tables(message["content"], message["role"])
            st.divider()
    else:
        st.info("Нажмите кнопку слева для добавления тестового JSON")

# Отладочная информация
st.divider()
st.markdown("### 🔍 Отладочная информация")

with st.expander("Показать исходный JSON"):
    st.code(test_json, language="json")

with st.expander("Проверка JSON парсинга"):
    try:
        parsed_data = json.loads(test_json)
        st.success(f"✅ JSON валиден. Найдено {len(parsed_data)} элементов")
        
        # Показываем статистику
        categories = {}
        text_elements = 0
        for item in parsed_data:
            category = item.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            if item.get('text', '').strip():
                text_elements += 1
        
        st.write(f"**Элементов с текстом:** {text_elements}")
        st.write(f"**Категории:** {list(categories.keys())}")
        st.write(f"**Распределение:** {categories}")
        
    except Exception as e:
        st.error(f"❌ Ошибка парсинга JSON: {e}")

st.markdown("""
### 📋 Что тестируем:

**Исходные данные из чата:**
```
[{"bbox": [189, 85, 234, 104], "category": "Text", "text": "RUS"}, ...]
```

**Ожидаемый результат:**
- Красивая HTML таблица с 14 строками
- Синие заголовки с белым текстом
- Чередующиеся цвета строк (белый/голубой)
- BBOX координаты в моноширинном шрифте
- Статистика: 14 элементов, 12 с текстом, 5 категорий

### 🚀 Если этот тест прошел:
Основное приложение будет правильно отображать JSON ответы dots.ocr как красивые таблицы!
""")