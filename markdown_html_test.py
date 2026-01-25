#!/usr/bin/env python3
"""
ТЕСТ HTML TO MARKDOWN КОНВЕРТЕРА
Запуск: streamlit run markdown_html_test.py --server.port 8513
"""

import streamlit as st
import re

def render_message_with_markdown_tables(content: str, role: str = "assistant"):
    """
    КОНВЕРТАЦИЯ HTML ТАБЛИЦ В MARKDOWN
    Если HTML не работает, используем markdown таблицы
    """
    
    if role == "assistant" and '<table' in content.lower() and '</table>' in content.lower():
        # Пытаемся сначала HTML
        try:
            # Простые встроенные стили
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
            
        except Exception as e:
            # Если HTML не работает, конвертируем в markdown
            st.warning("⚠️ HTML не работает, конвертируем в markdown")
            
            # Конвертируем HTML таблицу в markdown
            markdown_content = convert_html_table_to_markdown(content)
            st.markdown("📊 **Markdown таблица:**")
            st.markdown(markdown_content)
            st.info("✅ Markdown рендеринг")
    else:
        # Обычное сообщение
        st.markdown(content)

def convert_html_table_to_markdown(content: str) -> str:
    """Конвертирует HTML таблицу в markdown"""
    
    # Извлекаем все таблицы
    table_pattern = r'<table[^>]*>(.*?)</table>'
    tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
    
    result_content = content
    
    for table_html in tables:
        try:
            # Извлекаем строки
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(row_pattern, table_html, re.DOTALL | re.IGNORECASE)
            
            markdown_rows = []
            is_header = True
            
            for row in rows:
                # Извлекаем ячейки (th или td)
                cell_pattern = r'<t[hd][^>]*>(.*?)</t[hd]>'
                cells = re.findall(cell_pattern, row, re.DOTALL | re.IGNORECASE)
                
                if not cells:
                    continue
                
                # Очищаем содержимое ячеек
                clean_cells = []
                for cell in cells:
                    clean_cell = re.sub(r'<[^>]+>', '', cell)  # Убираем HTML теги
                    clean_cell = clean_cell.strip().replace('\n', ' ')
                    # Ограничиваем длину
                    if len(clean_cell) > 30:
                        clean_cell = clean_cell[:27] + "..."
                    clean_cells.append(clean_cell)
                
                # Формируем строку markdown
                markdown_row = "| " + " | ".join(clean_cells) + " |"
                markdown_rows.append(markdown_row)
                
                # Добавляем разделитель после заголовка
                if is_header and len(clean_cells) > 0:
                    separator = "| " + " | ".join(["---"] * len(clean_cells)) + " |"
                    markdown_rows.append(separator)
                    is_header = False
            
            # Создаем markdown таблицу
            markdown_table = "\n\n" + "\n".join(markdown_rows) + "\n\n"
            
            # Заменяем HTML таблицу на markdown
            full_table_pattern = f'<table[^>]*>{re.escape(table_html)}</table>'
            result_content = re.sub(full_table_pattern, markdown_table, result_content, flags=re.IGNORECASE)
            
        except Exception as e:
            # Если конвертация не удалась, просто убираем HTML теги
            clean_table = re.sub(r'<[^>]+>', '', table_html)
            result_content = result_content.replace(f'<table>{table_html}</table>', f"\n\n**📊 Таблица:**\n{clean_table}\n\n")
    
    return result_content

# Настройка страницы
st.set_page_config(
    page_title="HTML to Markdown Test",
    page_icon="📊",
    layout="wide"
)

# Заголовок
st.title("📊 Тест HTML → Markdown конвертера")
st.markdown("**Если HTML не работает, используем markdown таблицы**")

# Тестовый HTML контент
test_html = """📋 Анализ документа<table class="bbox-table">
<thead>
<tr>
<th>#</th>
<th>Категория</th>
<th>Координаты</th>
<th>Текст</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Title</td>
<td>[50, 10, 400, 40]</td>
<td>ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ</td>
</tr>
<tr>
<td>2</td>
<td>Text</td>
<td>[50, 50, 300, 70]</td>
<td>1. ИВАНОВ ИВАН ИВАНОВИЧ</td>
</tr>
<tr>
<td>3</td>
<td>Text</td>
<td>[50, 80, 200, 100]</td>
<td>2. ИВАН ИВАНОВИЧ</td>
</tr>
<tr>
<td>4</td>
<td>Text</td>
<td>[50, 110, 150, 130]</td>
<td>3. 15.03.1985</td>
</tr>
</tbody>
</table>

Конвертация завершена."""

# Инициализация сообщений
if "markdown_test_messages" not in st.session_state:
    st.session_state.markdown_test_messages = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("🧪 Тестирование конвертера")
    
    if st.button("➕ Добавить HTML таблицу", use_container_width=True):
        st.session_state.markdown_test_messages.append({
            "role": "assistant",
            "content": test_html
        })
        st.rerun()
    
    if st.button("🗑️ Очистить", use_container_width=True):
        st.session_state.markdown_test_messages = []
        st.rerun()
    
    st.divider()
    
    st.markdown("### 🎯 Что должно произойти:")
    st.markdown("""
    **Вариант 1 (HTML работает):**
    - Сообщение "HTML таблица"
    - Зеленые заголовки
    - Сообщение "HTML рендеринг"
    
    **Вариант 2 (HTML не работает):**
    - Сообщение "HTML не работает, конвертируем в markdown"
    - Сообщение "Markdown таблица"
    - Обычная markdown таблица
    - Сообщение "Markdown рендеринг"
    
    **В любом случае таблица должна быть читаемой!**
    """)

with col2:
    st.subheader("📊 Результат")
    
    if st.session_state.markdown_test_messages:
        for i, message in enumerate(st.session_state.markdown_test_messages):
            st.markdown(f"**Тест #{i+1}:**")
            with st.chat_message(message["role"]):
                render_message_with_markdown_tables(message["content"], message["role"])
            st.divider()
    else:
        st.info("Нажмите кнопку слева для добавления тестовой таблицы")

# Отладочная информация
st.divider()
st.markdown("### 🔍 Отладочная информация")

with st.expander("Показать исходный HTML"):
    st.code(test_html, language="html")

with st.expander("Показать конвертированный markdown"):
    markdown_result = convert_html_table_to_markdown(test_html)
    st.code(markdown_result, language="markdown")

st.markdown("""
### 📋 Преимущества этого подхода:

1. **Двойная защита:** Сначала пытается HTML, потом markdown
2. **Всегда работает:** Markdown поддерживается везде
3. **Читаемость:** В любом случае таблица будет видна
4. **Отладка:** Показывает, какой метод используется

### 🚀 Если этот тест прошел:
Основное приложение будет работать в любом случае!
""")
