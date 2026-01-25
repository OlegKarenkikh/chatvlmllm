#!/usr/bin/env python3
"""
ТЕСТОВОЕ ПРИЛОЖЕНИЕ ДЛЯ ПРОВЕРКИ HTML РЕНДЕРИНГА
Запуск: streamlit run test_html_emergency.py --server.port 8510
"""

import streamlit as st

def render_message_content_ultimate(content: str, role: str = "assistant"):
    """
    МАКСИМАЛЬНО НАДЕЖНЫЙ HTML РЕНДЕРИНГ С ПРАВИЛЬНЫМИ ЦВЕТАМИ
    Гарантированно читаемые цвета без проблем контрастности
    """
    
    # Принудительная проверка HTML
    has_html_table = bool(
        '<table' in content.lower() and 
        '</table>' in content.lower()
    )
    
    if role == "assistant" and has_html_table:
        # ПРИНУДИТЕЛЬНЫЙ HTML РЕНДЕРИНГ с контрастными цветами
        
        # Добавляем CSS стили с правильной контрастностью
        styled_content = f"""
        <div style="margin: 10px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <style>
                .emergency-html-table {{
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 15px 0 !important;
                    font-size: 14px !important;
                    border: 2px solid #333 !important;
                    background-color: #ffffff !important;
                }}
                .emergency-html-table th {{
                    background-color: #2c3e50 !important;
                    color: #ffffff !important;
                    font-weight: bold !important;
                    padding: 12px 8px !important;
                    text-align: left !important;
                    border: 1px solid #34495e !important;
                }}
                .emergency-html-table td {{
                    padding: 10px 8px !important;
                    border: 1px solid #bdc3c7 !important;
                    text-align: left !important;
                    background-color: #ffffff !important;
                    color: #2c3e50 !important;
                }}
                .emergency-html-table tr:nth-child(even) td {{
                    background-color: #f8f9fa !important;
                    color: #2c3e50 !important;
                }}
                .emergency-html-table tr:hover td {{
                    background-color: #e9ecef !important;
                    color: #2c3e50 !important;
                }}
                .bbox-table {{
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 15px 0 !important;
                    font-size: 14px !important;
                    border: 2px solid #333 !important;
                    background-color: #ffffff !important;
                }}
                .bbox-table th {{
                    background-color: #1565c0 !important;
                    color: #ffffff !important;
                    font-weight: bold !important;
                    padding: 12px 8px !important;
                    text-align: left !important;
                    border: 1px solid #0d47a1 !important;
                }}
                .bbox-table td {{
                    padding: 10px 8px !important;
                    border: 1px solid #bdc3c7 !important;
                    text-align: left !important;
                    background-color: #ffffff !important;
                    color: #2c3e50 !important;
                }}
                .bbox-table tr:nth-child(even) td {{
                    background-color: #f1f8ff !important;
                    color: #2c3e50 !important;
                }}
                .bbox-table tr:hover td {{
                    background-color: #e3f2fd !important;
                    color: #1565c0 !important;
                }}
                
                /* Дополнительные стили для лучшей читаемости */
                .emergency-html-table, .bbox-table {{
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                    border-radius: 4px !important;
                    overflow: hidden !important;
                }}
                
                /* Убираем любые конфликтующие стили Streamlit */
                .emergency-html-table *, .bbox-table * {{
                    color: inherit !important;
                }}
            </style>
            {content.replace('class="bbox-table"', 'class="bbox-table emergency-html-table"')}
        </div>
        """
        
        # ПРИНУДИТЕЛЬНОЕ отображение с HTML
        st.markdown("🔧 **HTML таблица с улучшенными цветами**")
        st.markdown(styled_content, unsafe_allow_html=True)
        st.success("✅ HTML рендеринг с контрастными цветами применен")
        
    else:
        # Обычное сообщение
        st.markdown(content)

# Настройка страницы
st.set_page_config(
    page_title="HTML Emergency Test",
    page_icon="🚨",
    layout="wide"
)

# Заголовок
st.title("🚨 Экстренный тест HTML рендеринга")

# Тестовый HTML контент
test_html = """📋 Детальная информация<table class="bbox-table">
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
<td>Text</td>
<td>[100, 200, 300, 250]</td>
<td>Пример текста документа</td>
</tr>
<tr>
<td>2</td>
<td>Title</td>
<td>[50, 50, 400, 100]</td>
<td>Заголовок документа</td>
</tr>
<tr>
<td>3</td>
<td>Picture</td>
<td>[200, 300, 500, 400]</td>
<td>Изображение в документе</td>
</tr>
</tbody>
</table>

Анализ завершен успешно."""

# Инициализация сообщений
if "test_messages" not in st.session_state:
    st.session_state.test_messages = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("🧪 Тестирование")
    
    if st.button("➕ Добавить тестовое сообщение с HTML"):
        st.session_state.test_messages.append({
            "role": "assistant",
            "content": test_html
        })
        st.rerun()
    
    if st.button("🗑️ Очистить сообщения"):
        st.session_state.test_messages = []
        st.rerun()

with col2:
    st.subheader("📊 Результат")
    
    if st.session_state.test_messages:
        for i, message in enumerate(st.session_state.test_messages):
            with st.chat_message(message["role"]):
                render_message_content_ultimate(message["content"], message["role"])
    else:
        st.info("Нажмите кнопку слева чтобы добавить тестовое сообщение")

# Инструкции
st.divider()
st.markdown("""
### 🔍 Что проверить:

1. **Нажмите "Добавить тестовое сообщение с HTML"**
2. **Проверьте результат справа:**
   - ✅ Должна появиться красивая таблица с зелеными заголовками
   - ✅ Должны быть сообщения "HTML таблица обнаружена" и "HTML рендеринг применен"
   - ❌ НЕ должно быть сырого HTML кода

3. **Если таблица отображается правильно** - исправление работает!
4. **Если видите HTML код** - проблема в браузере или Streamlit

### 🚀 Следующие шаги:
- Если тест прошел успешно, основное приложение тоже должно работать
- Если тест не прошел, проблема глубже (браузер, Streamlit, система)
""")
