#!/usr/bin/env python3
"""
Чистое исправление HTML рендеринга - удаляем дубликаты и создаем правильную функцию
"""

# Читаем app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Удаляем все старые функции
import re

# Удаляем все дублированные функции display_message_with_html_support
pattern = r'def display_message_with_html_support\(.*?\n(?:.*?\n)*?.*?st\.markdown\(content\)\n'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Удаляем другие старые функции
patterns_to_remove = [
    r'def render_chat_content_with_html\(.*?\n(?:.*?\n)*?.*?st\.markdown\(remaining_text\)\n',
    r'def render_chat_content_with_html_v2\(.*?\n(?:.*?\n)*?.*?st\.markdown\(styled_table, unsafe_allow_html=True\)\n',
    r'def render_html_content_ultimate\(.*?\n(?:.*?\n)*?.*?st\.markdown\(current_content\)\n'
]

for pattern in patterns_to_remove:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Создаем одну правильную функцию
correct_function = '''
def display_message_with_html_support(content: str):
    """Правильное отображение сообщений с поддержкой HTML таблиц"""
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
    content = content[:import_end] + correct_function + content[import_end:]

# Записываем обратно
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Чистое исправление HTML рендеринга применено!')
print('🔄 Перезагрузите приложение для применения изменений')