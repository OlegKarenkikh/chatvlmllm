#!/usr/bin/env python3
"""
Тест HTML таблиц в реальном чате с принудительной перезагрузкой модулей
"""

import streamlit as st
import importlib
import sys

# Принудительная перезагрузка модулей
if 'utils.smart_content_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.smart_content_renderer'])
if 'utils.html_table_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.html_table_renderer'])

from utils.smart_content_renderer import SmartContentRenderer

def main():
    st.title("🔧 Тест HTML таблиц в реальном чате")
    
    # Инициализация сессии
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Кнопка для добавления тестового сообщения с HTML таблицей
    if st.button("➕ Добавить тестовое сообщение с HTML таблицей"):
        test_message = {
            "role": "assistant",
            "content": """📋 Детальная информация
<table class="bbox-table">
    <thead>
        <tr>
            <th style="width: 50px;">#</th>
            <th style="width: 150px;">Категория</th>
            <th style="width: 200px;">BBOX координаты</th>
            <th>Текст</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>Заголовок документа</td>
            <td>[45, 123, 567, 189]</td>
            <td>ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ</td>
        </tr>
        <tr>
            <td>2</td>
            <td>Персональные данные</td>
            <td>[78, 234, 456, 298]</td>
            <td>ИВАНОВ ИВАН ИВАНОВИЧ</td>
        </tr>
        <tr>
            <td>3</td>
            <td>Дата рождения</td>
            <td>[123, 345, 389, 412]</td>
            <td>15.03.1985</td>
        </tr>
    </tbody>
</table>

Анализ завершен. Найдено 3 текстовых блока с координатами."""
        }
        st.session_state.messages.append(test_message)
        st.rerun()
    
    # Кнопка очистки чата
    if st.button("🗑️ Очистить чат"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Отображение чата - точно как в реальном приложении
    st.subheader("💬 Чат")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Точно такой же код как в app.py
                SmartContentRenderer.render_content_smart(message["content"])
            else:
                SmartContentRenderer.render_content_smart(message["content"])
    
    # Диагностика
    st.divider()
    st.subheader("🔍 Диагностика")
    
    if st.session_state.messages:
        last_message = st.session_state.messages[-1]
        
        # Проверка определения HTML
        has_html = SmartContentRenderer.has_html_content(last_message["content"])
        st.write(f"**HTML обнаружен в последнем сообщении:** {has_html}")
        
        if has_html:
            content_info = SmartContentRenderer.extract_html_and_text(last_message["content"])
            st.write(f"**Найдено таблиц:** {len(content_info['tables'])}")
            
            if content_info['tables']:
                st.success("✅ Таблица найдена и должна отображаться")
                with st.expander("Показать извлеченную таблицу"):
                    st.code(content_info['tables'][0])
            else:
                st.error("❌ Таблица не найдена")
        else:
            st.error("❌ HTML не обнаружен")
    
    # Тест рендеринга вне чата
    st.divider()
    st.subheader("🧪 Тест рендеринга вне чата")
    
    test_html = """<table style="border-collapse: collapse; width: 100%;">
    <thead>
        <tr>
            <th style="border: 1px solid #ddd; padding: 8px; background-color: #f8f9fa; color: #333;">#</th>
            <th style="border: 1px solid #ddd; padding: 8px; background-color: #f8f9fa; color: #333;">Тест</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px; color: #333;">1</td>
            <td style="border: 1px solid #ddd; padding: 8px; color: #333;">Данные</td>
        </tr>
    </tbody>
</table>"""
    
    st.markdown("**Прямой HTML рендеринг:**")
    st.markdown(test_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()