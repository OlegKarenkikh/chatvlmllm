#!/usr/bin/env python3
"""
Окончательное исправление HTML рендеринга в чате
"""

import streamlit as st
import re

def main():
    st.title("🔧 Окончательное исправление HTML рендеринга")
    
    st.info("""
    **Проблема:** HTML таблицы в чате отображаются как код вместо таблиц
    
    **Решение:** Принудительная замена логики отображения сообщений
    """)
    
    # Тестовый контент с HTML таблицей
    test_content = """Результат анализа документа:

📋 Детальная информация<table class="bbox-table">
<thead>
<tr>
<th>Элемент</th>
<th>Категория</th>
<th>Координаты</th>
<th>Текст</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Text</td>
<td>[100, 200, 300, 250]</td>
<td>Пример текста</td>
</tr>
<tr>
<td>2</td>
<td>Title</td>
<td>[50, 50, 400, 100]</td>
<td>Заголовок документа</td>
</tr>
</tbody>
</table>

Анализ завершен."""

    st.subheader("🧪 Тест нового рендеринга")
    
    # Новая функция рендеринга
    def render_html_content_ultimate(content: str):
        """Окончательное решение для HTML рендеринга"""
        
        # Поиск HTML таблиц
        table_pattern = r'<table[^>]*>.*?</table>'
        tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not tables:
            st.markdown(content)
            return
        
        # Обрабатываем каждую таблицу
        current_content = content
        
        for i, table_html in enumerate(tables):
            # Находим позицию таблицы
            table_pos = current_content.find(table_html)
            
            # Текст до таблицы
            before_table = current_content[:table_pos]
            if before_table.strip():
                st.markdown(before_table)
            
            # Отображаем таблицу
            st.markdown(f"**📊 Таблица {i+1}:**")
            
            # Создаем стилизованную таблицу
            styled_html = f"""
            <div style="overflow-x: auto; margin: 10px 0;">
                <style>
                    .ultimate-table {{
                        border-collapse: collapse;
                        width: 100%;
                        font-size: 13px;
                        margin: 0;
                    }}
                    .ultimate-table th {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px;
                        text-align: left;
                        border: 1px solid #ddd;
                    }}
                    .ultimate-table td {{
                        padding: 8px;
                        border: 1px solid #ddd;
                        text-align: left;
                    }}
                    .ultimate-table tr:nth-child(even) {{
                        background-color: #f2f2f2;
                    }}
                    .ultimate-table tr:hover {{
                        background-color: #f5f5f5;
                    }}
                </style>
                {table_html.replace('class="bbox-table"', 'class="ultimate-table"')}
            </div>
            """
            
            # Отображаем HTML
            st.markdown(styled_html, unsafe_allow_html=True)
            
            # Обновляем контент
            current_content = current_content[table_pos + len(table_html):]
        
        # Оставшийся текст
        if current_content.strip():
            st.markdown(current_content)
    
    # Тестируем
    with st.chat_message("assistant"):
        render_html_content_ultimate(test_content)
    
    st.success("✅ Если таблица отображается правильно, исправление работает!")
    
    # Кнопка для применения исправления
    if st.button("🚀 Применить исправление к app.py", type="primary"):
        apply_ultimate_fix()
        st.success("✅ Исправление применено! Перезагрузите приложение.")
        st.balloons()

def apply_ultimate_fix():
    """Применяет окончательное исправление к app.py"""
    
    # Читаем app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Новая функция
    new_function = '''
def render_html_content_ultimate(content: str):
    """Окончательное решение для HTML рендеринга"""
    
    # Поиск HTML таблиц
    table_pattern = r'<table[^>]*>.*?</table>'
    tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not tables:
        st.markdown(content)
        return
    
    # Обрабатываем каждую таблицу
    current_content = content
    
    for i, table_html in enumerate(tables):
        # Находим позицию таблицы
        table_pos = current_content.find(table_html)
        
        # Текст до таблицы
        before_table = current_content[:table_pos]
        if before_table.strip():
            st.markdown(before_table)
        
        # Отображаем таблицу
        st.markdown(f"**📊 Таблица {i+1}:**")
        
        # Создаем стилизованную таблицу
        styled_html = f"""
        <div style="overflow-x: auto; margin: 10px 0;">
            <style>
                .ultimate-table {{
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 13px;
                    margin: 0;
                }}
                .ultimate-table th {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                .ultimate-table td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                    text-align: left;
                }}
                .ultimate-table tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .ultimate-table tr:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
            {table_html.replace('class="bbox-table"', 'class="ultimate-table"')}
        </div>
        """
        
        # Отображаем HTML
        st.markdown(styled_html, unsafe_allow_html=True)
        
        # Обновляем контент
        current_content = current_content[table_pos + len(table_html):]
    
    # Оставшийся текст
    if current_content.strip():
        st.markdown(current_content)

'''
    
    # Вставляем функцию
    import_pos = content.find('from ui.styles import get_custom_css')
    if import_pos != -1:
        import_end = content.find('\n', import_pos) + 1
        content = content[:import_end] + new_function + content[import_end:]
    
    # Заменяем все вызовы
    content = content.replace('render_chat_content_with_html_v2(', 'render_html_content_ultimate(')
    content = content.replace('render_chat_content_with_html(', 'render_html_content_ultimate(')
    
    # Записываем
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    main()