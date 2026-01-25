#!/usr/bin/env python3
"""
Финальный тест исправлений HTML таблиц и дублирования режимов
"""

import streamlit as st
import re
import html

def render_html_tables_simple(content: str) -> str:
    """Простая замена HTML таблиц на markdown"""
    
    # Поиск HTML таблиц
    table_pattern = r'<table[^>]*>.*?</table>'
    tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not tables:
        return content
    
    result_content = content
    
    for table_html in tables:
        try:
            # Конвертируем HTML таблицу в markdown
            markdown_table = html_table_to_markdown(table_html)
            
            # Заменяем HTML таблицу на markdown
            result_content = result_content.replace(table_html, f"\n\n**📊 Таблица:**\n\n{markdown_table}\n\n")
            
        except Exception as e:
            # Fallback - просто убираем HTML теги
            clean_table = re.sub(r'<[^>]+>', '', table_html)
            result_content = result_content.replace(table_html, f"\n\n**📊 Таблица:**\n{clean_table}\n\n")
    
    return result_content

def html_table_to_markdown(table_html: str) -> str:
    """Конвертация HTML таблицы в Markdown"""
    
    try:
        # Извлечение строк таблицы
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
        
        if not rows:
            return "Не удалось извлечь строки таблицы"
        
        markdown_rows = []
        is_header = True
        
        for row in rows:
            # Извлечение ячеек
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL | re.IGNORECASE)
            
            if not cells:
                continue
            
            # Очистка содержимого ячеек от HTML тегов
            clean_cells = []
            for cell in cells:
                clean_cell = re.sub(r'<[^>]+>', '', cell)
                clean_cell = html.unescape(clean_cell).strip()
                # Ограничиваем длину ячейки
                if len(clean_cell) > 50:
                    clean_cell = clean_cell[:47] + "..."
                clean_cells.append(clean_cell)
            
            # Формирование строки Markdown
            markdown_row = "| " + " | ".join(clean_cells) + " |"
            markdown_rows.append(markdown_row)
            
            # Добавление разделителя после заголовка
            if is_header and len(clean_cells) > 0:
                separator = "| " + " | ".join(["---"] * len(clean_cells)) + " |"
                markdown_rows.append(separator)
                is_header = False
        
        return "\n".join(markdown_rows)
        
    except Exception as e:
        return f"Ошибка конвертации таблицы: {str(e)}"

def main():
    st.title("🔧 Финальный тест исправлений")
    
    # Инициализация сессии
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Тестовое сообщение с HTML таблицей
    test_message_content = """📋 Детальная информация<table class="bbox-table">         <thead>             <tr>                 <th style="width: 50px;">#</th>                 <th style="width: 150px;">Категория</th>                 <th style="width: 200px;">BBOX координаты</th>                 <th>Текст</th>             </tr>         </thead>         <tbody>             <tr>                 <td>1</td>                 <td>Заголовок документа</td>                 <td>[45, 123, 567, 189]</td>                 <td>ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ</td>             </tr>             <tr>                 <td>2</td>                 <td>Персональные данные</td>                 <td>[78, 234, 456, 298]</td>                 <td>ИВАНОВ ИВАН ИВАНОВИЧ</td>             </tr>         </tbody>     </table>

Анализ завершен."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Добавить сообщение с HTML таблицей"):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": test_message_content
            })
            st.rerun()
        
        if st.button("🗑️ Очистить чат"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        st.write("**Статус исправлений:**")
        st.success("✅ Дублирование режимов убрано")
        st.success("✅ HTML рендеринг заменен на простую функцию")
        st.info(f"Сообщений в чате: {len(st.session_state.messages)}")
    
    st.divider()
    
    # Отображение чата с новой функцией
    st.subheader("💬 Чат с исправленным рендерингом")
    
    chat_container = st.container(height=400)
    
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Нажмите кнопку выше, чтобы добавить тестовое сообщение!")
        
        # Display chat messages с новой функцией
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                # Используем новую простую функцию
                processed_content = render_html_tables_simple(message["content"])
                st.markdown(processed_content)
    
    st.divider()
    
    # Сравнение до и после
    st.subheader("🔍 Сравнение до и после")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**❌ Было (сырой HTML):**")
        st.code(test_message_content[:200] + "...")
    
    with col2:
        st.write("**✅ Стало (markdown таблица):**")
        if st.session_state.messages:
            processed = render_html_tables_simple(test_message_content)
            st.markdown(processed[:300] + "...")

if __name__ == "__main__":
    main()