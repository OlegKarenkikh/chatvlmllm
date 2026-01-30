#!/usr/bin/env python3
"""
Добавление детального логирования в app.py для отладки HTML рендеринга
"""

import datetime

# Читаем app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Добавляем импорт для логирования в начало файла
logging_imports = '''import streamlit as st
import yaml
from pathlib import Path
from PIL import Image
import io
import re
import sys
import importlib
import html
import datetime
import os

# ЛОГИРОВАНИЕ HTML РЕНДЕРИНГА
def log_html_debug(message, content_preview=""):
    """Детальное логирование для отладки HTML"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_msg = f"🔍 [{timestamp}] HTML_DEBUG: {message}"
    if content_preview:
        log_msg += f" | Контент: {content_preview[:100]}..."
    print(log_msg)  # В консоль
    # Также в Streamlit если возможно
    try:
        if hasattr(st, 'session_state') and hasattr(st.session_state, 'html_debug_logs'):
            st.session_state.html_debug_logs.append(log_msg)
        else:
            if not hasattr(st, 'session_state'):
                pass  # Еще не инициализирован
            else:
                st.session_state.html_debug_logs = [log_msg]
    except:
        pass  # Игнорируем ошибки логирования

'''

# Заменяем начальные импорты
old_imports = '''import streamlit as st
import yaml
from pathlib import Path
from PIL import Image
import io
import re
import sys
import importlib
import html'''

if old_imports in content:
    content = content.replace(old_imports, logging_imports)
    print("✅ Добавлены импорты для логирования")

# Добавляем логирование в секцию отображения сообщений
old_chat_section = '''            # Display chat messages - НОВАЯ ЛОГИКА HTML РЕНДЕРИНГА
            for i, message in enumerate(st.session_state.messages):
                with st.chat_message(message["role"]):
                    if message["role"] == "assistant":
                        # ПРИНУДИТЕЛЬНАЯ ОБРАБОТКА HTML ТАБЛИЦ
                        content = message["content"]
                        
                        # Проверяем наличие HTML таблиц
                        if '<table' in content and '</table>' in content:
                            # ПРИНУДИТЕЛЬНО отображаем HTML
                            st.markdown("🔧 **Обнаружена HTML таблица - отображаем с HTML поддержкой**")
                            st.markdown(content, unsafe_allow_html=True)
                        else:
                            # Обычное сообщение
                            st.markdown(content)'''

new_chat_section = '''            # Display chat messages - НОВАЯ ЛОГИКА HTML РЕНДЕРИНГА С ЛОГИРОВАНИЕМ
            log_html_debug(f"🚀 НАЧАЛО ОТОБРАЖЕНИЯ СООБЩЕНИЙ: Всего {len(st.session_state.messages)} сообщений")
            
            for i, message in enumerate(st.session_state.messages):
                log_html_debug(f"📝 Сообщение #{i+1}: роль={message['role']}, длина={len(message['content'])}")
                
                with st.chat_message(message["role"]):
                    if message["role"] == "assistant":
                        # ПРИНУДИТЕЛЬНАЯ ОБРАБОТКА HTML ТАБЛИЦ
                        content = message["content"]
                        
                        # ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ
                        log_html_debug(f"🔍 Анализ сообщения #{i+1}", content[:200])
                        
                        has_table_start = '<table' in content
                        has_table_end = '</table>' in content
                        has_html_table = has_table_start and has_table_end
                        
                        log_html_debug(f"📊 HTML проверка: <table={has_table_start}, </table>={has_table_end}, итог={has_html_table}")
                        
                        # Проверяем наличие HTML таблиц
                        if has_html_table:
                            # ПРИНУДИТЕЛЬНО отображаем HTML
                            log_html_debug("✅ ИСПОЛЬЗУЕМ HTML РЕНДЕРИНГ с unsafe_allow_html=True")
                            st.markdown("🔧 **[ЛОГИРОВАНИЕ] Обнаружена HTML таблица - отображаем с HTML поддержкой**")
                            st.markdown(f"🔍 **[DEBUG]** Файл: app.py, Время: {datetime.datetime.now().strftime('%H:%M:%S')}")
                            st.markdown(content, unsafe_allow_html=True)
                            log_html_debug("✅ HTML рендеринг выполнен")
                        else:
                            # Обычное сообщение
                            log_html_debug("📝 Используем обычный markdown")
                            st.markdown(content)'''

# Заменяем секцию
if old_chat_section in content:
    content = content.replace(old_chat_section, new_chat_section)
    print("✅ Добавлено логирование в отображение сообщений")
else:
    print("❌ Секция отображения сообщений не найдена")

# Добавляем логирование в отображение ответов в реальном времени
old_response_section = '''# ПРИНУДИТЕЛЬНАЯ ОБРАБОТКА HTML В ОТВЕТАХ
                        if '<table' in response and '</table>' in response:
                            st.markdown("🔧 **HTML таблица в ответе - отображаем с HTML поддержкой**")
                            st.markdown(response, unsafe_allow_html=True)
                        else:
                            st.markdown(response)'''

new_response_section = '''# ПРИНУДИТЕЛЬНАЯ ОБРАБОТКА HTML В ОТВЕТАХ С ЛОГИРОВАНИЕМ
                        log_html_debug("🔄 Обработка нового ответа", response[:200])
                        
                        has_table = '<table' in response and '</table>' in response
                        log_html_debug(f"📊 Ответ содержит HTML таблицу: {has_table}")
                        
                        if has_table:
                            log_html_debug("✅ НОВЫЙ ОТВЕТ: Используем HTML рендеринг")
                            st.markdown("🔧 **[ЛОГИРОВАНИЕ] HTML таблица в ответе - отображаем с HTML поддержкой**")
                            st.markdown(f"🔍 **[DEBUG]** Новый ответ, Время: {datetime.datetime.now().strftime('%H:%M:%S')}")
                            st.markdown(response, unsafe_allow_html=True)
                            log_html_debug("✅ HTML рендеринг нового ответа выполнен")
                        else:
                            log_html_debug("📝 Новый ответ: обычный markdown")
                            st.markdown(response)'''

# Заменяем секцию ответов
content = content.replace(old_response_section, new_response_section)
print("✅ Добавлено логирование в отображение ответов")

# Добавляем отображение логов в сайдбар
sidebar_logs = '''
    # Отображение логов отладки HTML
    if hasattr(st.session_state, 'html_debug_logs') and st.session_state.html_debug_logs:
        with st.expander("🔍 Логи HTML рендеринга", expanded=False):
            st.caption("Последние 10 записей:")
            for log_entry in st.session_state.html_debug_logs[-10:]:
                st.code(log_entry, language="text")
            
            if st.button("🗑️ Очистить логи"):
                st.session_state.html_debug_logs = []
                st.rerun()
    
    st.divider()
'''

# Вставляем логи в сайдбар перед "Project stats"
project_stats_pos = content.find('st.markdown("### 📊 Статистика проекта")')
if project_stats_pos != -1:
    content = content[:project_stats_pos] + sidebar_logs + content[project_stats_pos:]
    print("✅ Добавлено отображение логов в сайдбар")

# Записываем обратно
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Детальное логирование добавлено в app.py!')
print('🔍 Теперь будут видны все этапы HTML обработки')
print('📊 Логи отображаются в сайдбаре в разделе "Логи HTML рендеринга"')
print('🔄 Перезагрузите приложение для применения изменений')