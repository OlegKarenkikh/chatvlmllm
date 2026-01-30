#!/usr/bin/env python3
"""
Исправление отступов в app.py
"""

# Читаем app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Исправляем проблемные места с отступами
fixes = [
    # Исправляем отступы для HTML проверки
    ('if \'<table\' in message["content"] and \'</table>\' in message["content"]:\n                                st.markdown(message["content"], unsafe_allow_html=True)\n                            else:\n                                st.markdown(message["content"])',
     '''if '<table' in message["content"] and '</table>' in message["content"]:
                                st.markdown(message["content"], unsafe_allow_html=True)
                            else:
                                st.markdown(message["content"])'''),
    
    ('if \'<table\' in response and \'</table>\' in response:\n                        st.markdown(response, unsafe_allow_html=True)\n                    else:\n                        st.markdown(response)',
     '''if '<table' in response and '</table>' in response:
                            st.markdown(response, unsafe_allow_html=True)
                        else:
                            st.markdown(response)''')
]

# Применяем исправления
for old, new in fixes:
    content = content.replace(old, new)

# Записываем обратно
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Отступы исправлены!')
print('🔄 Перезагрузите приложение')