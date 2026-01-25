#!/usr/bin/env python3
"""
Тест простого исправления HTML рендеринга
"""

import streamlit as st

def display_message_with_html_support(content: str):
    """Простое отображение сообщений с поддержкой HTML таблиц"""
    if '<table' in content and '</table>' in content:
        # Есть HTML таблица - отображаем с unsafe_allow_html=True
        st.markdown(content, unsafe_allow_html=True)
    else:
        # Обычное сообщение
        st.markdown(content)

def main():
    st.title("🧪 Тест простого исправления HTML")
    
    # Тестовый контент
    test_html = """Результат анализа:

📋 Детальная информация<table class="bbox-table" style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">
<thead>
<tr style="background-color: #f2f2f2;">
<th style="border: 1px solid #ddd; padding: 8px;">Элемент</th>
<th style="border: 1px solid #ddd; padding: 8px;">Категория</th>
<th style="border: 1px solid #ddd; padding: 8px;">Координаты</th>
<th style="border: 1px solid #ddd; padding: 8px;">Текст</th>
</tr>
</thead>
<tbody>
<tr>
<td style="border: 1px solid #ddd; padding: 8px;">1</td>
<td style="border: 1px solid #ddd; padding: 8px;">Text</td>
<td style="border: 1px solid #ddd; padding: 8px;">[100, 200, 300, 250]</td>
<td style="border: 1px solid #ddd; padding: 8px;">Пример текста</td>
</tr>
<tr style="background-color: #f9f9f9;">
<td style="border: 1px solid #ddd; padding: 8px;">2</td>
<td style="border: 1px solid #ddd; padding: 8px;">Title</td>
<td style="border: 1px solid #ddd; padding: 8px;">[50, 50, 400, 100]</td>
<td style="border: 1px solid #ddd; padding: 8px;">Заголовок документа</td>
</tr>
</tbody>
</table>

Анализ завершен успешно."""

    st.subheader("🔧 Старый способ (проблемный)")
    st.markdown("Обычный st.markdown():")
    st.markdown(test_html)  # HTML как текст
    
    st.subheader("✅ Новый способ (исправленный)")
    st.markdown("С новой функцией:")
    display_message_with_html_support(test_html)  # HTML как таблица
    
    st.subheader("💬 Имитация чата")
    with st.chat_message("assistant"):
        display_message_with_html_support(test_html)
    
    if st.button("🎉 Если таблица отображается правильно - исправление работает!"):
        st.balloons()
        st.success("✅ HTML рендеринг исправлен!")

if __name__ == "__main__":
    main()