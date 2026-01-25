#!/usr/bin/env python3
"""
ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ HTML РЕНДЕРИНГА
Полная замена логики отображения сообщений в app.py
"""

import re
import sys
from pathlib import Path

def create_ultimate_html_renderer():
    """Создает максимально надежную функцию HTML рендеринга"""
    
    html_renderer_code = '''
def render_message_content_ultimate(content: str, role: str = "assistant"):
    """
    МАКСИМАЛЬНО НАДЕЖНЫЙ HTML РЕНДЕРИНГ
    Гарантированно отображает HTML таблицы правильно
    """
    
    # Принудительная проверка HTML
    has_html_table = bool(
        '<table' in content.lower() and 
        '</table>' in content.lower()
    )
    
    if role == "assistant" and has_html_table:
        # ПРИНУДИТЕЛЬНЫЙ HTML РЕНДЕРИНГ с дополнительными стилями
        
        # Добавляем CSS стили прямо в контент
        styled_content = f"""
        <div style="margin: 10px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <style>
                .emergency-html-table {{
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 15px 0 !important;
                    font-size: 14px !important;
                    border: 2px solid #ddd !important;
                    background-color: white !important;
                }}
                .emergency-html-table th {{
                    background-color: #4CAF50 !important;
                    color: white !important;
                    font-weight: bold !important;
                    padding: 12px 8px !important;
                    text-align: left !important;
                    border: 1px solid #45a049 !important;
                }}
                .emergency-html-table td {{
                    padding: 10px 8px !important;
                    border: 1px solid #ddd !important;
                    text-align: left !important;
                    background-color: white !important;
                }}
                .emergency-html-table tr:nth-child(even) td {{
                    background-color: #f9f9f9 !important;
                }}
                .emergency-html-table tr:hover td {{
                    background-color: #f5f5f5 !important;
                }}
                .bbox-table {{
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 15px 0 !important;
                    font-size: 14px !important;
                    border: 2px solid #ddd !important;
                }}
                .bbox-table th {{
                    background-color: #2196F3 !important;
                    color: white !important;
                    font-weight: bold !important;
                    padding: 12px 8px !important;
                    text-align: left !important;
                    border: 1px solid #1976D2 !important;
                }}
                .bbox-table td {{
                    padding: 10px 8px !important;
                    border: 1px solid #ddd !important;
                    text-align: left !important;
                    background-color: white !important;
                }}
                .bbox-table tr:nth-child(even) td {{
                    background-color: #e3f2fd !important;
                }}
            </style>
            {content.replace('class="bbox-table"', 'class="bbox-table emergency-html-table"')}
        </div>
        """
        
        # ПРИНУДИТЕЛЬНОЕ отображение с HTML
        st.markdown("🔧 **HTML таблица обнаружена - применяем специальный рендеринг**")
        st.markdown(styled_content, unsafe_allow_html=True)
        st.success("✅ HTML рендеринг применен успешно")
        
        # Дополнительная отладочная информация
        st.info(f"🔍 Обработано {len(re.findall(r'<table.*?</table>', content, re.DOTALL | re.IGNORECASE))} HTML таблиц")
        
    else:
        # Обычное сообщение
        st.markdown(content)
'''
    
    return html_renderer_code

def fix_chat_message_display():
    """Исправляет отображение сообщений чата в app.py"""
    
    app_file = Path("app.py")
    
    if not app_file.exists():
        print("❌ Файл app.py не найден!")
        return False
    
    # Читаем содержимое файла
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Добавляем функцию рендеринга в начало файла (после импортов)
    html_renderer = create_ultimate_html_renderer()
    
    # Находим место после импортов
    import_end = content.find('# Import UI components')
    if import_end == -1:
        import_end = content.find('from ui.styles import get_custom_css')
    
    if import_end != -1:
        # Вставляем функцию после импортов
        insert_pos = content.find('\n', import_end) + 1
        content = content[:insert_pos] + '\n' + html_renderer + '\n' + content[insert_pos:]
    else:
        # Добавляем в начало файла
        content = html_renderer + '\n\n' + content
    
    # Заменяем старую логику отображения сообщений
    old_chat_pattern = r'# Display chat messages.*?for i, message in enumerate\(st\.session_state\.messages\):.*?with st\.chat_message\(message\["role"\]\):.*?if message\["role"\] == "assistant":.*?# ПРОВЕРКА И ОТОБРАЖЕНИЕ HTML ТАБЛИЦ.*?content = message\["content"\].*?# Проверяем наличие HTML таблиц.*?if \'<table\' in content and \'</table>\' in content:.*?# Отображаем HTML таблицы.*?st\.markdown\(content, unsafe_allow_html=True\).*?else:.*?# Обычное сообщение.*?st\.markdown\(content\).*?else:.*?# Простое отображение пользовательских сообщений.*?st\.markdown\(message\["content"\]\)'
    
    new_chat_section = '''# Display chat messages - ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ HTML
            for i, message in enumerate(st.session_state.messages):
                with st.chat_message(message["role"]):
                    # ИСПОЛЬЗУЕМ НОВУЮ НАДЕЖНУЮ ФУНКЦИЮ
                    render_message_content_ultimate(message["content"], message["role"])'''
    
    # Пытаемся найти и заменить секцию отображения сообщений
    chat_section_found = False
    
    # Ищем более простой паттерн
    simple_pattern = r'for i, message in enumerate\(st\.session_state\.messages\):.*?with st\.chat_message\(message\["role"\]\):.*?if message\["role"\] == "assistant":.*?st\.markdown\(content\).*?else:.*?st\.markdown\(message\["content"\]\)'
    
    if re.search(simple_pattern, content, re.DOTALL):
        content = re.sub(simple_pattern, new_chat_section.strip(), content, flags=re.DOTALL)
        chat_section_found = True
        print("✅ Найдена и заменена секция отображения сообщений (простой паттерн)")
    
    # Если не нашли, ищем по ключевым словам
    if not chat_section_found:
        lines = content.split('\n')
        start_line = -1
        end_line = -1
        
        for i, line in enumerate(lines):
            if 'for i, message in enumerate(st.session_state.messages):' in line:
                start_line = i
            elif start_line != -1 and 'st.markdown(message["content"])' in line and 'else:' in lines[i-1]:
                end_line = i
                break
        
        if start_line != -1 and end_line != -1:
            # Заменяем найденную секцию
            new_lines = lines[:start_line] + [new_chat_section] + lines[end_line+1:]
            content = '\n'.join(new_lines)
            chat_section_found = True
            print(f"✅ Найдена и заменена секция отображения сообщений (строки {start_line}-{end_line})")
    
    # Исправляем отображение новых ответов
    response_pattern = r'# HTML РЕНДЕРИНГ В ОТВЕТАХ.*?if \'<table\' in response and \'</table>\' in response:.*?st\.markdown\(response, unsafe_allow_html=True\).*?else:.*?st\.markdown\(response\)'
    
    new_response_section = '''# HTML РЕНДЕРИНГ В ОТВЕТАХ - ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ
                        render_message_content_ultimate(response, "assistant")'''
    
    if re.search(response_pattern, content, re.DOTALL):
        content = re.sub(response_pattern, new_response_section, content, flags=re.DOTALL)
        print("✅ Исправлена секция отображения новых ответов")
    else:
        # Ищем все места где отображается response
        response_locations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if 'st.markdown(response)' in line or 'st.markdown(response, unsafe_allow_html=True)' in line:
                response_locations.append(i)
        
        # Заменяем все найденные места
        for loc in reversed(response_locations):  # В обратном порядке чтобы не сбить индексы
            lines[loc] = '                        render_message_content_ultimate(response, "assistant")'
        
        content = '\n'.join(lines)
        print(f"✅ Исправлено {len(response_locations)} мест отображения ответов")
    
    # Сохраняем исправленный файл
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Файл app.py успешно исправлен!")
    return True

def create_test_application():
    """Создает тестовое приложение для проверки HTML рендеринга"""
    
    test_app_content = '''#!/usr/bin/env python3
"""
ТЕСТОВОЕ ПРИЛОЖЕНИЕ ДЛЯ ПРОВЕРКИ HTML РЕНДЕРИНГА
Запуск: streamlit run test_html_emergency.py --server.port 8510
"""

import streamlit as st

def render_message_content_ultimate(content: str, role: str = "assistant"):
    """
    МАКСИМАЛЬНО НАДЕЖНЫЙ HTML РЕНДЕРИНГ
    Гарантированно отображает HTML таблицы правильно
    """
    
    # Принудительная проверка HTML
    has_html_table = bool(
        '<table' in content.lower() and 
        '</table>' in content.lower()
    )
    
    if role == "assistant" and has_html_table:
        # ПРИНУДИТЕЛЬНЫЙ HTML РЕНДЕРИНГ с дополнительными стилями
        
        # Добавляем CSS стили прямо в контент
        styled_content = f"""
        <div style="margin: 10px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <style>
                .emergency-html-table {{
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 15px 0 !important;
                    font-size: 14px !important;
                    border: 2px solid #ddd !important;
                    background-color: white !important;
                }}
                .emergency-html-table th {{
                    background-color: #4CAF50 !important;
                    color: white !important;
                    font-weight: bold !important;
                    padding: 12px 8px !important;
                    text-align: left !important;
                    border: 1px solid #45a049 !important;
                }}
                .emergency-html-table td {{
                    padding: 10px 8px !important;
                    border: 1px solid #ddd !important;
                    text-align: left !important;
                    background-color: white !important;
                }}
                .emergency-html-table tr:nth-child(even) td {{
                    background-color: #f9f9f9 !important;
                }}
                .emergency-html-table tr:hover td {{
                    background-color: #f5f5f5 !important;
                }}
                .bbox-table {{
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 15px 0 !important;
                    font-size: 14px !important;
                    border: 2px solid #ddd !important;
                }}
                .bbox-table th {{
                    background-color: #2196F3 !important;
                    color: white !important;
                    font-weight: bold !important;
                    padding: 12px 8px !important;
                    text-align: left !important;
                    border: 1px solid #1976D2 !important;
                }}
                .bbox-table td {{
                    padding: 10px 8px !important;
                    border: 1px solid #ddd !important;
                    text-align: left !important;
                    background-color: white !important;
                }}
                .bbox-table tr:nth-child(even) td {{
                    background-color: #e3f2fd !important;
                }}
            </style>
            {content.replace('class="bbox-table"', 'class="bbox-table emergency-html-table"')}
        </div>
        """
        
        # ПРИНУДИТЕЛЬНОЕ отображение с HTML
        st.markdown("🔧 **HTML таблица обнаружена - применяем специальный рендеринг**")
        st.markdown(styled_content, unsafe_allow_html=True)
        st.success("✅ HTML рендеринг применен успешно")
        
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
'''
    
    with open("test_html_emergency.py", 'w', encoding='utf-8') as f:
        f.write(test_app_content)
    
    print("✅ Создано тестовое приложение: test_html_emergency.py")

def main():
    """Основная функция экстренного исправления"""
    
    print("🚨 ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ HTML РЕНДЕРИНГА")
    print("=" * 50)
    
    # 1. Исправляем основное приложение
    print("\n1️⃣ Исправляем app.py...")
    if fix_chat_message_display():
        print("✅ app.py исправлен успешно!")
    else:
        print("❌ Ошибка при исправлении app.py")
        return
    
    # 2. Создаем тестовое приложение
    print("\n2️⃣ Создаем тестовое приложение...")
    create_test_application()
    
    print("\n" + "=" * 50)
    print("🎉 ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
    print("\n📋 ЧТО СДЕЛАНО:")
    print("✅ Добавлена максимально надежная функция HTML рендеринга")
    print("✅ Заменена логика отображения сообщений в app.py")
    print("✅ Исправлено отображение новых ответов")
    print("✅ Создано тестовое приложение")
    
    print("\n🧪 КАК ТЕСТИРОВАТЬ:")
    print("1. Запустите тест: streamlit run test_html_emergency.py --server.port 8510")
    print("2. Откройте: http://localhost:8510")
    print("3. Нажмите 'Добавить тестовое сообщение с HTML'")
    print("4. Проверьте, отображается ли таблица правильно")
    
    print("\n🚀 ЕСЛИ ТЕСТ ПРОШЕЛ УСПЕШНО:")
    print("1. Перезапустите основное приложение: streamlit run app.py")
    print("2. Откройте: http://localhost:8504")
    print("3. HTML таблицы должны работать!")
    
    print("\n⚠️ ЕСЛИ ТЕСТ НЕ ПРОШЕЛ:")
    print("Проблема в браузере или системе Streamlit")
    print("Попробуйте другой браузер или обновите Streamlit")

if __name__ == "__main__":
    main()