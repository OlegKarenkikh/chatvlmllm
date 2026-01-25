#!/usr/bin/env python3
"""
Полная переписка логики HTML рендеринга в app.py
"""

# Читаем app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим секцию отображения сообщений чата и полностью переписываем
old_chat_section = '''            # Display chat messages
            for i, message in enumerate(st.session_state.messages):
                with st.chat_message(message["role"]):
                    if message["role"] == "assistant":
                        # Проверяем, есть ли результат OCR для обработки
                        if (hasattr(st.session_state, 'last_ocr_result') and 
                            i == len(st.session_state.messages) - 1):  # Последнее сообщение
                            
                            ocr_result = st.session_state.last_ocr_result
                            prompt_info = ocr_result.get("prompt_info", {})
                            
                            # Правильное отображение контента с поддержкой HTML таблиц
                            if '<table' in message["content"] and '</table>' in message["content"]:
                                st.markdown(message["content"], unsafe_allow_html=True)
                            else:
                                st.markdown(message["content"])
                            
                            # Обработка BBOX если включена
                            display_bbox_visualization_improved(ocr_result)
                        else:
                            # Правильное отображение сообщения с поддержкой HTML таблиц
                            if '<table' in message["content"] and '</table>' in message["content"]:
                                st.markdown(message["content"], unsafe_allow_html=True)
                            else:
                                st.markdown(message["content"])
                    else:
                        # Простое отображение пользовательских сообщений
                        st.markdown(message["content"])'''

new_chat_section = '''            # Display chat messages - НОВАЯ ЛОГИКА HTML РЕНДЕРИНГА
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
                            st.markdown(content)
                        
                        # Проверяем, есть ли результат OCR для обработки
                        if (hasattr(st.session_state, 'last_ocr_result') and 
                            i == len(st.session_state.messages) - 1):  # Последнее сообщение
                            
                            ocr_result = st.session_state.last_ocr_result
                            # Обработка BBOX если включена
                            display_bbox_visualization_improved(ocr_result)
                    else:
                        # Простое отображение пользовательских сообщений
                        st.markdown(message["content"])'''

# Заменяем секцию
if old_chat_section in content:
    content = content.replace(old_chat_section, new_chat_section)
    print("✅ Секция отображения сообщений заменена")
else:
    print("❌ Секция не найдена - возможно, код уже изменен")

# Также заменяем отображение ответов в реальном времени
old_response_patterns = [
    '''if '<table' in response and '</table>' in response:
                            st.markdown(response, unsafe_allow_html=True)
                        else:
                            st.markdown(response)''',
    '''if '<table' in response and '</table>' in response:
                        st.markdown(response, unsafe_allow_html=True)
                    else:
                        st.markdown(response)'''
]

new_response_code = '''# ПРИНУДИТЕЛЬНАЯ ОБРАБОТКА HTML В ОТВЕТАХ
                        if '<table' in response and '</table>' in response:
                            st.markdown("🔧 **HTML таблица в ответе - отображаем с HTML поддержкой**")
                            st.markdown(response, unsafe_allow_html=True)
                        else:
                            st.markdown(response)'''

for old_pattern in old_response_patterns:
    if old_pattern in content:
        content = content.replace(old_pattern, new_response_code)
        print("✅ Отображение ответов обновлено")

# Записываем обратно
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Полная переписка HTML логики завершена!')
print('🔧 Добавлены отладочные сообщения для диагностики')
print('🔄 Перезагрузите основное приложение')