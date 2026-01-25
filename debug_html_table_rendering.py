#!/usr/bin/env python3
"""
Отладка проблемы с рендерингом HTML таблиц в чате
"""

import streamlit as st
from utils.smart_content_renderer import SmartContentRenderer
from utils.html_table_renderer import HTMLTableRenderer

def main():
    st.title("🔧 Отладка HTML таблиц в чате")
    
    # Тестовый контент с HTML таблицей (как в проблеме пользователя)
    test_content = """📋 Детальная информация
<table class="bbox-table">
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
            <td>Заголовок</td>
            <td>[100, 200, 300, 400]</td>
            <td>Пример текста</td>
        </tr>
        <tr>
            <td>2</td>
            <td>Содержимое</td>
            <td>[150, 250, 350, 450]</td>
            <td>Другой текст</td>
        </tr>
    </tbody>
</table>

Дополнительная информация после таблицы."""

    st.subheader("🧪 Тестовый контент:")
    st.code(test_content)
    
    st.divider()
    
    # Тест 1: Проверка определения HTML
    st.subheader("🔍 Тест 1: Определение HTML")
    has_html = SmartContentRenderer.has_html_content(test_content)
    st.write(f"HTML обнаружен: **{has_html}**")
    
    # Тест 2: Анализ контента
    st.subheader("📊 Тест 2: Анализ контента")
    content_info = SmartContentRenderer.extract_html_and_text(test_content)
    st.write(f"Найдено таблиц: **{len(content_info['tables'])}**")
    st.write(f"Есть HTML: **{content_info['has_html']}**")
    
    if content_info['tables']:
        st.write("**Найденные таблицы:**")
        for i, table in enumerate(content_info['tables']):
            with st.expander(f"Таблица {i+1}"):
                st.code(table)
    
    st.divider()
    
    # Тест 3: Рендеринг через SmartContentRenderer
    st.subheader("🎨 Тест 3: Умный рендеринг")
    try:
        SmartContentRenderer.render_content_smart(test_content)
        st.success("✅ Умный рендеринг выполнен успешно")
    except Exception as e:
        st.error(f"❌ Ошибка умного рендеринга: {e}")
        st.exception(e)
    
    st.divider()
    
    # Тест 4: Прямой рендеринг HTML таблицы
    st.subheader("🔧 Тест 4: Прямой рендеринг HTML")
    if content_info['tables']:
        try:
            renderer = HTMLTableRenderer()
            renderer.render_table_in_streamlit(content_info['tables'][0], "Тестовая таблица")
            st.success("✅ Прямой рендеринг выполнен успешно")
        except Exception as e:
            st.error(f"❌ Ошибка прямого рендеринга: {e}")
            st.exception(e)
    
    st.divider()
    
    # Тест 5: Fallback рендеринг
    st.subheader("🛡️ Тест 5: Fallback рендеринг")
    if content_info['tables']:
        st.markdown("**📊 Таблица (fallback):**")
        st.markdown(content_info['tables'][0], unsafe_allow_html=True)
        st.success("✅ Fallback рендеринг выполнен успешно")
    
    st.divider()
    
    # Тест 6: Обычный markdown
    st.subheader("📝 Тест 6: Обычный markdown (как сейчас отображается)")
    st.markdown(test_content)

if __name__ == "__main__":
    main()