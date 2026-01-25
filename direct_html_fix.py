#!/usr/bin/env python3
"""
Прямое исправление HTML рендеринга в app.py
"""

# Читаем app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем все вызовы display_message_with_html_support на прямой код
replacements = [
    # В отображении сообщений чата
    ('display_message_with_html_support(message["content"])', 
     '''if '<table' in message["content"] and '</table>' in message["content"]:
                                st.markdown(message["content"], unsafe_allow_html=True)
                            else:
                                st.markdown(message["content"])'''),
    
    # В отображении ответов
    ('display_message_with_html_support(response)', 
     '''if '<table' in response and '</table>' in response:
                        st.markdown(response, unsafe_allow_html=True)
                    else:
                        st.markdown(response)''')
]

# Применяем замены
for old, new in replacements:
    content = content.replace(old, new)

# Записываем обратно
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Прямое исправление HTML рендеринга применено!')
print('🔄 Перезагрузите приложение')