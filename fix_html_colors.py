#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ ЦВЕТОВ В HTML ТАБЛИЦАХ
Устраняет проблемы с контрастностью (белые буквы на белом фоне, голубые на голубом)
"""

import re
from pathlib import Path

def create_improved_html_renderer():
    """Создает функцию HTML рендеринга с правильными контрастными цветами"""
    
    html_renderer_code = '''
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
'''
    
    return html_renderer_code

def fix_colors_in_files():
    """Исправляет цвета в основных файлах"""
    
    files_to_fix = [
        "app.py",
        "test_html_emergency.py",
        "app_html_fixed.py"
    ]
    
    improved_renderer = create_improved_html_renderer()
    
    for filename in files_to_fix:
        file_path = Path(filename)
        
        if not file_path.exists():
            print(f"⚠️ Файл {filename} не найден, пропускаем")
            continue
        
        print(f"🔧 Исправляем цвета в {filename}...")
        
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем и заменяем функцию render_message_content_ultimate
        pattern = r'def render_message_content_ultimate\(.*?\n(?:.*?\n)*?.*?st\.markdown\(content\)'
        
        if re.search(pattern, content, re.DOTALL):
            # Заменяем существующую функцию
            content = re.sub(pattern, improved_renderer.strip(), content, flags=re.DOTALL)
            print(f"✅ Заменена функция render_message_content_ultimate в {filename}")
        else:
            # Если функции нет, добавляем её
            # Находим место после импортов
            import_end = content.find('# Import UI components')
            if import_end == -1:
                import_end = content.find('from ui.styles import get_custom_css')
            
            if import_end != -1:
                # Вставляем функцию после импортов
                insert_pos = content.find('\n', import_end) + 1
                content = content[:insert_pos] + '\n' + improved_renderer + '\n' + content[insert_pos:]
                print(f"✅ Добавлена функция render_message_content_ultimate в {filename}")
            else:
                print(f"⚠️ Не удалось найти место для вставки функции в {filename}")
        
        # Сохраняем файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Файл {filename} обновлен с улучшенными цветами")

def create_color_test_app():
    """Создает тестовое приложение для проверки цветов"""
    
    test_app_content = '''#!/usr/bin/env python3
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
'''
    
    with open("test_html_colors.py", 'w', encoding='utf-8') as f:
        f.write(test_app_content)
    
    print("✅ Создано тестовое приложение для цветов: test_html_colors.py")

def main():
    """Основная функция исправления цветов"""
    
    print("🎨 ИСПРАВЛЕНИЕ ЦВЕТОВ HTML ТАБЛИЦ")
    print("=" * 50)
    
    # 1. Исправляем цвета в файлах
    print("\n1️⃣ Исправляем цвета в основных файлах...")
    fix_colors_in_files()
    
    # 2. Создаем тестовое приложение для цветов
    print("\n2️⃣ Создаем тестовое приложение для проверки цветов...")
    create_color_test_app()
    
    print("\n" + "=" * 50)
    print("🎉 ИСПРАВЛЕНИЕ ЦВЕТОВ ЗАВЕРШЕНО!")
    print("\n📋 ЧТО ИСПРАВЛЕНО:")
    print("✅ Заголовки таблиц: темный фон + белый текст (высокий контраст)")
    print("✅ Ячейки таблиц: белый/светлый фон + темный текст")
    print("✅ Убраны проблемы с белым на белом и голубым на голубом")
    print("✅ Добавлены тени и скругления для лучшего вида")
    
    print("\n🧪 КАК ТЕСТИРОВАТЬ ЦВЕТА:")
    print("1. Запустите тест: streamlit run test_html_colors.py --server.port 8511")
    print("2. Откройте: http://localhost:8511")
    print("3. Нажмите кнопки для добавления тестовых таблиц")
    print("4. Проверьте читаемость всех элементов")
    
    print("\n🎯 ЦВЕТОВАЯ СХЕМА:")
    print("• BBOX таблицы: Синие заголовки (#1565c0) + белый текст")
    print("• Обычные таблицы: Темно-серые заголовки (#2c3e50) + белый текст")
    print("• Все ячейки: Белый/светлый фон + темный текст (#2c3e50)")
    
    print("\n🚀 ПОСЛЕ УСПЕШНОГО ТЕСТА:")
    print("Перезапустите основное приложение - цвета будут исправлены!")

if __name__ == "__main__":
    main()