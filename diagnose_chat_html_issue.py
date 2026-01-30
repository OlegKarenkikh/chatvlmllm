#!/usr/bin/env python3
"""
Диагностика проблемы с HTML таблицами в реальном чате
"""

import streamlit as st
import sys
import importlib

# Принудительная перезагрузка модулей при каждом запуске
if 'utils.smart_content_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.smart_content_renderer'])
if 'utils.html_table_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.html_table_renderer'])

from utils.smart_content_renderer import SmartContentRenderer

def main():
    st.title("🔍 Диагностика HTML таблиц в чате")
    
    # Инициализация сессии
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Тестовое сообщение с HTML таблицей
    test_message_content = """📋 Детальная информация<table class="bbox-table">         <thead>             <tr>                 <th style="width: 50px;">#</th>                 <th style="width: 150px;">Категория</th>                 <th style="width: 200px;">BBOX координаты</th>                 <th>Текст</th>             </tr>         </thead>         <tbody>             <tr>                 <td>1</td>                 <td>Заголовок документа</td>                 <td>[45, 123, 567, 189]</td>                 <td>ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ</td>             </tr>             <tr>                 <td>2</td>                 <td>Персональные данные</td>                 <td>[78, 234, 456, 298]</td>                 <td>ИВАНОВ ИВАН ИВАНОВИЧ</td>             </tr>         </tbody>     </table>

Анализ завершен."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Добавить сообщение с HTML"):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": test_message_content
            })
            st.rerun()
        
        if st.button("🗑️ Очистить чат"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        # Диагностика текущего состояния
        st.write("**Состояние:**")
        st.write(f"Сообщений в чате: {len(st.session_state.messages)}")
        
        if st.session_state.messages:
            last_msg = st.session_state.messages[-1]
            has_html = SmartContentRenderer.has_html_content(last_msg["content"])
            st.write(f"HTML в последнем сообщении: {has_html}")
    
    st.divider()
    
    # Отображение чата - ТОЧНО как в app.py
    st.subheader("💬 Чат (как в реальном приложении)")
    
    chat_container = st.container(height=400)
    
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Нажмите кнопку выше, чтобы добавить тестовое сообщение!")
        
        # Display chat messages - ТОЧНО как в app.py
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    # Проверяем, есть ли результат OCR для обработки
                    if (hasattr(st.session_state, 'last_ocr_result') and 
                        i == len(st.session_state.messages) - 1):  # Последнее сообщение
                        
                        st.write("🔧 **DEBUG:** Используется ветка с last_ocr_result")
                        ocr_result = st.session_state.last_ocr_result
                        
                        # Умное отображение контента с автоматической обработкой HTML
                        SmartContentRenderer.render_content_smart(message["content"])
                        
                        # Обработка BBOX если включена (закомментируем для теста)
                        # display_bbox_visualization_improved(ocr_result)
                    else:
                        st.write("🔧 **DEBUG:** Используется обычная ветка")
                        # Умное отображение сообщения с автоматической обработкой HTML
                        SmartContentRenderer.render_content_smart(message["content"])
                else:
                    # Умное отображение пользовательских сообщений
                    SmartContentRenderer.render_content_smart(message["content"])
    
    st.divider()
    
    # Дополнительные тесты
    st.subheader("🧪 Дополнительные тесты")
    
    # Тест 1: Прямой рендеринг
    with st.expander("Тест 1: Прямой рендеринг SmartContentRenderer"):
        st.write("**Результат прямого рендеринга:**")
        try:
            SmartContentRenderer.render_content_smart(test_message_content)
            st.success("✅ Прямой рендеринг работает")
        except Exception as e:
            st.error(f"❌ Ошибка прямого рендеринга: {e}")
    
    # Тест 2: Обычный markdown
    with st.expander("Тест 2: Обычный markdown (для сравнения)"):
        st.write("**Результат обычного markdown:**")
        st.markdown(test_message_content)
    
    # Тест 3: HTML с unsafe_allow_html
    with st.expander("Тест 3: HTML с unsafe_allow_html"):
        st.write("**Результат HTML рендеринга:**")
        # Извлекаем только таблицу
        import re
        table_match = re.search(r'<table[^>]*>.*?</table>', test_message_content, re.DOTALL)
        if table_match:
            table_html = table_match.group(0)
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.error("Таблица не найдена")

if __name__ == "__main__":
    main()