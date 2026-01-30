#!/usr/bin/env python3
"""
Тест исправления HTML рендеринга в чате
"""

import streamlit as st
import re

def clean_html_table(table_html: str) -> str:
    """Очистка и улучшение HTML таблицы для отображения в Streamlit"""
    
    # Добавляем CSS стили для лучшего отображения
    styled_table = f"""
    <style>
    .bbox-table {{
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
        font-size: 14px;
    }}
    .bbox-table th, .bbox-table td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }}
    .bbox-table th {{
        background-color: #f2f2f2;
        font-weight: bold;
    }}
    .bbox-table tr:nth-child(even) {{
        background-color: #f9f9f9;
    }}
    </style>
    {table_html}
    """
    
    return styled_table

def render_chat_content_with_html(content: str) -> None:
    """Правильное отображение контента чата с поддержкой HTML таблиц"""
    
    # Поиск HTML таблиц
    table_pattern = r'<table[^>]*>.*?</table>'
    tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not tables:
        # Нет HTML таблиц - обычное отображение
        st.markdown(content)
        return
    
    # Есть HTML таблицы - разбиваем контент на части
    current_pos = 0
    
    for table_html in tables:
        # Находим позицию таблицы
        table_start = content.find(table_html, current_pos)
        
        # Отображаем текст до таблицы
        if table_start > current_pos:
            text_before = content[current_pos:table_start]
            if text_before.strip():
                st.markdown(text_before)
        
        # Отображаем HTML таблицу
        st.markdown("**📊 Детальная информация**")
        try:
            # Очищаем и улучшаем HTML таблицу
            clean_table = clean_html_table(table_html)
            st.markdown(clean_table, unsafe_allow_html=True)
        except Exception as e:
            # Fallback - показываем ошибку
            st.error(f"Ошибка отображения таблицы: {e}")
            st.code(table_html)
        
        # Обновляем позицию
        current_pos = table_start + len(table_html)
    
    # Отображаем оставшийся текст после последней таблицы
    if current_pos < len(content):
        remaining_text = content[current_pos:]
        if remaining_text.strip():
            st.markdown(remaining_text)

def main():
    st.title("🧪 Тест исправления HTML рендеринга в чате")
    
    # Тестовый контент с HTML таблицей
    test_content = """Вот результат анализа документа:

📋 Детальная информация<table class="bbox-table">         <thead>             <tr>                 <th>Элемент</th>                 <th>Категория</th>                 <th>Координаты</th>                 <th>Текст</th>             </tr>         </thead>         <tbody>             <tr>                 <td>1</td>                 <td>Text</td>                 <td>[100, 200, 300, 250]</td>                 <td>Пример текста</td>             </tr>             <tr>                 <td>2</td>                 <td>Title</td>                 <td>[50, 50, 400, 100]</td>                 <td>Заголовок документа</td>             </tr>         </tbody>     </table>

Анализ завершен успешно."""

    st.subheader("🔧 Старый способ (проблемный)")
    st.markdown("Так отображалось раньше (HTML как текст):")
    st.code(test_content)
    
    st.subheader("✅ Новый способ (исправленный)")
    st.markdown("Так отображается теперь:")
    
    # Имитируем чат
    with st.chat_message("assistant"):
        render_chat_content_with_html(test_content)
    
    st.subheader("📊 Сравнение")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**❌ Старый способ:**")
        st.markdown(test_content)  # HTML отображается как текст
    
    with col2:
        st.markdown("**✅ Новый способ:**")
        render_chat_content_with_html(test_content)  # HTML отображается правильно
    
    st.success("🎉 HTML таблицы теперь отображаются правильно!")
    
    st.info("""
    **Что исправлено:**
    
    1. ✅ HTML таблицы теперь отображаются как таблицы, а не как код
    2. ✅ Добавлены CSS стили для красивого отображения
    3. ✅ Сохранена обратная совместимость
    4. ✅ Обработка ошибок при рендеринге HTML
    """)

if __name__ == "__main__":
    main()