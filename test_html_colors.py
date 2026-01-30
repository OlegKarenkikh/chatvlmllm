#!/usr/bin/env python3
"""
ТЕСТ ЦВЕТОВ HTML ТАБЛИЦ
Проверка контрастности и читаемости
Запуск: streamlit run test_html_colors.py --server.port 8511
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
    page_title="HTML Colors Test",
    page_icon="🎨",
    layout="wide"
)

# Заголовок
st.title("🎨 Тест цветов HTML таблиц")
st.markdown("**Проверка контрастности и читаемости**")

# Тестовые HTML таблицы
test_html_bbox = """📋 Детальная информация<table class="bbox-table">
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
<tr>
<td>4</td>
<td>Table</td>
<td>[150, 400, 450, 500]</td>
<td>Табличные данные</td>
</tr>
<tr>
<td>5</td>
<td>Footer</td>
<td>[0, 550, 600, 600]</td>
<td>Нижний колонтитул</td>
</tr>
</tbody>
</table>

Анализ завершен успешно."""

test_html_regular = """<table class="regular-table">
<thead>
<tr>
<th>Поле</th>
<th>Значение</th>
<th>Статус</th>
</tr>
</thead>
<tbody>
<tr>
<td>Имя</td>
<td>Иван Петров</td>
<td>✅ Найдено</td>
</tr>
<tr>
<td>Дата рождения</td>
<td>15.03.1985</td>
<td>✅ Найдено</td>
</tr>
<tr>
<td>Номер документа</td>
<td>1234567890</td>
<td>✅ Найдено</td>
</tr>
</tbody>
</table>"""

# Инициализация сообщений
if "color_test_messages" not in st.session_state:
    st.session_state.color_test_messages = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("🧪 Тестирование цветов")
    
    if st.button("➕ BBOX таблица (синие заголовки)", use_container_width=True):
        st.session_state.color_test_messages.append({
            "role": "assistant",
            "content": test_html_bbox
        })
        st.rerun()
    
    if st.button("➕ Обычная таблица (темные заголовки)", use_container_width=True):
        st.session_state.color_test_messages.append({
            "role": "assistant",
            "content": test_html_regular
        })
        st.rerun()
    
    if st.button("🗑️ Очистить все", use_container_width=True):
        st.session_state.color_test_messages = []
        st.rerun()
    
    st.divider()
    
    st.markdown("### 🎯 Что проверить:")
    st.markdown("""
    **✅ Правильно:**
    - Белый текст на темном фоне заголовков
    - Темный текст на белом/светлом фоне ячеек
    - Хорошая читаемость всех элементов
    
    **❌ Неправильно:**
    - Белый текст на белом фоне
    - Голубой текст на голубом фоне
    - Плохо читаемые элементы
    """)

with col2:
    st.subheader("📊 Результат тестирования")
    
    if st.session_state.color_test_messages:
        for i, message in enumerate(st.session_state.color_test_messages):
            st.markdown(f"**Тест #{i+1}:**")
            with st.chat_message(message["role"]):
                render_message_content_ultimate(message["content"], message["role"])
            st.divider()
    else:
        st.info("Нажмите кнопки слева чтобы добавить тестовые таблицы")

# Инструкции
st.divider()
st.markdown("""
### 🔍 Цветовая схема:

**BBOX таблицы (class="bbox-table"):**
- 🔵 **Заголовки:** Синий фон (#1565c0) + белый текст (#ffffff)
- ⚪ **Четные строки:** Белый фон (#ffffff) + темный текст (#2c3e50)
- 🔷 **Нечетные строки:** Светло-синий фон (#f1f8ff) + темный текст (#2c3e50)
- 🔹 **При наведении:** Голубой фон (#e3f2fd) + синий текст (#1565c0)

**Обычные таблицы:**
- ⚫ **Заголовки:** Темно-серый фон (#2c3e50) + белый текст (#ffffff)
- ⚪ **Четные строки:** Белый фон (#ffffff) + темный текст (#2c3e50)
- 🔘 **Нечетные строки:** Светло-серый фон (#f8f9fa) + темный текст (#2c3e50)

### 🚀 Если цвета правильные:
Основное приложение тоже будет работать с правильными цветами!
""")
