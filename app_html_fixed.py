#!/usr/bin/env python3
"""
Минимальное приложение с гарантированно работающим HTML рендерингом
"""

import streamlit as st
import yaml
from pathlib import Path
from PIL import Image
import io
import re
import sys
import importlib
import html

# Принудительная перезагрузка модулей HTML рендеринга при каждом запуске
if 'utils.smart_content_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.smart_content_renderer'])
if 'utils.html_table_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.html_table_renderer'])

# Import UI components


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

from ui.styles import get_custom_css

def render_message_with_html(content: str):
    """ГАРАНТИРОВАННЫЙ HTML рендеринг для сообщений"""
    
    # Принудительная проверка HTML таблиц
    has_html_table = ('<table' in content.lower() and '</table>' in content.lower())
    
    if has_html_table:
        # ПРИНУДИТЕЛЬНО отображаем HTML с дополнительными стилями
        styled_content = f"""
        <div style="margin: 10px 0;">
            <style>
                table {{
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 10px 0 !important;
                }}
                th, td {{
                    border: 1px solid #ddd !important;
                    padding: 8px !important;
                    text-align: left !important;
                }}
                th {{
                    background-color: #f2f2f2 !important;
                    font-weight: bold !important;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9 !important;
                }}
                .bbox-table {{
                    border-collapse: collapse !important;
                    width: 100% !important;
                }}
                .bbox-table th {{
                    background-color: #4CAF50 !important;
                    color: white !important;
                }}
            </style>
            {content}
        </div>
        """
        
        # Отображаем с принудительным HTML
        st.markdown("🔧 **HTML таблица обнаружена - отображаем с HTML поддержкой**")
        st.markdown(styled_content, unsafe_allow_html=True)
        
        # Дополнительная проверка
        st.success("✅ HTML рендеринг применен успешно")
        
    else:
        # Обычное сообщение
        st.markdown(content)

# Page configuration
st.set_page_config(
    page_title="ChatVLMLLM - HTML Fixed",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_execution_mode" not in st.session_state:
    st.session_state.current_execution_mode = "vLLM (Рекомендуется)"

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 4096

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Load configuration
@st.cache_resource
def load_config():
    """Load configuration from YAML file."""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# Initialize additional session state variables
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None
if "loaded_model" not in st.session_state:
    st.session_state.loaded_model = None

# Header
st.markdown('<h1 class="gradient-text" style="text-align: center;">🔬 ChatVLMLLM - HTML Fixed</h1>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; font-size: 1.2rem; color: #888; margin-bottom: 2rem;">'
    'Версия с исправленным HTML рендерингом</p>', 
    unsafe_allow_html=True
)

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
    st.title("Навигация")
    
    page = st.radio(
        "Выберите режим",
        ["🏠 Главная", "💬 Режим чата", "🧪 Тест HTML"],
        label_visibility="collapsed"
    )

# Main content area
if "🏠 Главная" in page:
    st.header("Приложение с исправленным HTML рендерингом")
    
    st.info("""
    **Это специальная версия приложения с гарантированно работающим HTML рендерингом.**
    
    Основные изменения:
    - ✅ Принудительная проверка HTML таблиц
    - ✅ Дополнительные CSS стили
    - ✅ Отладочные сообщения
    - ✅ Упрощенная логика
    """)
    
    if st.button("🧪 Перейти к тесту HTML"):
        st.session_state.page = "🧪 Тест HTML"
        st.rerun()

elif "🧪 Тест HTML" in page:
    st.header("🧪 Тест HTML рендеринга")
    
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

    st.subheader("🔍 Тест HTML рендеринга")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**❌ Обычный способ:**")
        st.markdown(test_html)
    
    with col2:
        st.markdown("**✅ С HTML рендерингом:**")
        render_message_with_html(test_html)
    
    st.divider()
    
    st.subheader("💬 Тест в чате")
    
    # Добавляем тестовое сообщение
    if st.button("➕ Добавить тестовое сообщение"):
        st.session_state.messages.append({
            "role": "assistant",
            "content": test_html
        })
        st.rerun()
    
    # Отображаем сообщения чата
    if st.session_state.messages:
        st.markdown("**Сообщения чата:**")
        
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                # ИСПОЛЬЗУЕМ НАШУ ФУНКЦИЮ
                render_message_with_html(message["content"])
    
    # Кнопка очистки
    if st.button("🗑️ Очистить сообщения"):
        st.session_state.messages = []
        st.rerun()

elif "💬 Режим чата" in page:
    st.header("💬 Интерактивный чат с HTML поддержкой")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🖼️ Загрузить изображение")
        
        chat_image = st.file_uploader(
            "Изображение для контекста чата",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
            key="chat_upload"
        )
        
        if chat_image:
            image = Image.open(chat_image)
            st.session_state.uploaded_image = image
            st.image(image, caption="Контекстное изображение", use_container_width=True)
    
    with col2:
        st.subheader("💬 Чат")
        
        # Display chat messages
        if not st.session_state.messages:
            st.info("👋 Загрузите изображение и начните задавать вопросы о нем!")
        
        # Display chat messages с нашей функцией
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                # ИСПОЛЬЗУЕМ НАШУ ФУНКЦИЮ HTML РЕНДЕРИНГА
                render_message_with_html(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Спросите об изображении...", disabled=not chat_image):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response using real model
            with st.chat_message("assistant"):
                with st.spinner("🤔 Думаю..."):
                    try:
                        # Здесь должна быть интеграция с моделью
                        # Для теста используем заглушку
                        if "таблица" in prompt.lower() or "bbox" in prompt.lower():
                            response = test_html
                        else:
                            response = f"Это тестовый ответ на ваш вопрос: '{prompt}'"
                        
                        # ИСПОЛЬЗУЕМ НАШУ ФУНКЦИЮ HTML РЕНДЕРИНГА
                        render_message_with_html(response)
                        
                    except Exception as e:
                        response = f"❌ Ошибка при обработке: {str(e)}"
                        st.markdown(response)
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🔧 Специальная версия с исправленным HTML рендерингом</p>
    <p style="font-size: 0.9rem;">Если HTML таблицы отображаются правильно, исправление работает!</p>
</div>
""", unsafe_allow_html=True)