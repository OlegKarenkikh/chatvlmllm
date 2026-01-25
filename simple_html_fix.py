#!/usr/bin/env python3
"""
Простое исправление HTML рендеринга
"""

# Читаем app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Простая функция для отображения HTML
simple_function = '''
def display_message_with_html_support(content: str):
    """Простое отображение сообщений с поддержкой HTML таблиц"""
    if '<table' in content and '</table>' in content:
        # Есть HTML таблица - отображаем с unsafe_allow_html=True
        st.markdown(content, unsafe_allow_html=True)
    else:
        # Обычное сообщение
        st.markdown(content)

'''

# Вставляем функцию после импортов
import_pos = content.find('from ui.styles import get_custom_css')
if import_pos != -1:
    import_end = content.find('\n', import_pos) + 1
    content = content[:import_end] + simple_function + content[import_end:]

# Заменяем все вызовы
content = content.replace('render_html_content_ultimate(', 'display_message_with_html_support(')
content = content.replace('render_chat_content_with_html_v2(', 'display_message_with_html_support(')
content = content.replace('render_chat_content_with_html(', 'display_message_with_html_support(')

# Записываем обратно
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Простое исправление HTML рендеринга применено!')
print('🔄 Перезагрузите приложение для применения изменений')