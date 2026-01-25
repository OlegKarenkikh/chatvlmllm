#!/usr/bin/env python3
"""
ПРОСТОЙ ТЕСТ HTML РЕНДЕРИНГА
Запуск: streamlit run simple_html_test.py --server.port 8512
"""

import streamlit as st

def render_message_content_simple(content: str, role: str = "assistant"):
    """
    ПРОСТОЙ И НАДЕЖНЫЙ HTML РЕНДЕРИНГ
    Без сложных стилей, только базовая функциональность
    """
    
    # Проверяем наличие HTML таблиц
    if role == "assistant" and '<table' in content.lower() and '</table>' in content.lower():
        # Простые встроенные стили прямо в HTML
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
        
        # Отображаем с HTML
        st.markdown("🔧 **Простой HTML рендеринг**")
        st.markdown(simple_styled_content, unsafe_allow_html=True)
        st.success("✅ HTML отображен")
        
    else:
        # Обычное сообщение
        st.markdown(content)

# Настройка страницы
st.set_page_config(
    page_title="Simple HTML Test",
    page_icon="🔧",
    layout="wide"
)

# Заголовок
st.title("🔧 Простой тест HTML")
st.markdown("**Минимальный подход без сложных стилей**")

# Тестовый HTML контент
test_html = """📋 Результат анализа<table class="bbox-table">
<thead>
<tr>
<th>#</th>
<th>Тип</th>
<th>Координаты</th>
<th>Содержимое</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Заголовок</td>
<td>[10, 20, 300, 50]</td>
<td>ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ</td>
</tr>
<tr>
<td>2</td>
<td>Текст</td>
<td>[10, 60, 200, 80]</td>
<td>1. ИВАНОВ ИВАН ИВАНОВИЧ</td>
</tr>
<tr>
<td>3</td>
<td>Дата</td>
<td>[10, 90, 150, 110]</td>
<td>3. 15.03.1985</td>
</tr>
</tbody>
</table>

Обработка завершена."""

# Инициализация сообщений
if "simple_test_messages" not in st.session_state:
    st.session_state.simple_test_messages = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("🧪 Простое тестирование")
    
    if st.button("➕ Добавить HTML таблицу", use_container_width=True):
        st.session_state.simple_test_messages.append({
            "role": "assistant",
            "content": test_html
        })
        st.rerun()
    
    if st.button("🗑️ Очистить", use_container_width=True):
        st.session_state.simple_test_messages = []
        st.rerun()
    
    st.divider()
    
    st.markdown("### 🎯 Что должно быть:")
    st.markdown("""
    **✅ Ожидаемый результат:**
    - Сообщение "Простой HTML рендеринг"
    - Таблица с зелеными заголовками
    - Белые ячейки с черным текстом
    - Сообщение "HTML отображен"
    
    **❌ Если не работает:**
    - Видите сырой HTML код
    - Нет зеленых заголовков
    - Нет сообщений подтверждения
    """)

with col2:
    st.subheader("📊 Результат")
    
    if st.session_state.simple_test_messages:
        for i, message in enumerate(st.session_state.simple_test_messages):
            st.markdown(f"**Тест #{i+1}:**")
            with st.chat_message(message["role"]):
                render_message_content_simple(message["content"], message["role"])
            st.divider()
    else:
        st.info("Нажмите кнопку слева для добавления тестовой таблицы")

# Отладочная информация
st.divider()
st.markdown("### 🔍 Отладочная информация")

with st.expander("Показать тестовый HTML код"):
    st.code(test_html, language="html")

st.markdown("""
### 📋 Инструкции:

1. **Нажмите "Добавить HTML таблицу"**
2. **Проверьте результат справа:**
   - Должна появиться таблица с зелеными заголовками
   - Должны быть сообщения подтверждения
3. **Если таблица отображается правильно** - исправление работает!
4. **Если видите HTML код** - проблема глубже

### 🚀 Если тест прошел:
Основное приложение тоже будет работать с простым HTML рендерингом.
""")
