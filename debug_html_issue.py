#!/usr/bin/env python3
"""
Отладка проблемы HTML рендеринга
"""

import streamlit as st

def main():
    st.title("🔍 Отладка HTML рендеринга")
    
    # Тестовый HTML контент - точно такой же как в проблеме
    problem_html = """📋 Детальная информация<table class="bbox-table">         <thead>             <tr>                 <th style="width: 50px;">#</th>                 <th style="width: 150px;">Категория</th>                 <th style="width: 200px;">BBOX координаты</th>                 <th>Текст</th>             </tr>         </thead>         <tbody>             <tr>                 <td>1</td>                 <td>Text</td>                 <td>[100, 200, 300, 250]</td>                 <td>Пример текста</td>             </tr>             <tr>                 <td>2</td>                 <td>Title</td>                 <td>[50, 50, 400, 100]</td>                 <td>Заголовок документа</td>             </tr>         </tbody>     </table>

Анализ завершен."""

    st.subheader("🧪 Тест 1: Обычный st.markdown()")
    st.markdown("**Результат без unsafe_allow_html:**")
    st.markdown(problem_html)
    
    st.divider()
    
    st.subheader("✅ Тест 2: st.markdown() с unsafe_allow_html=True")
    st.markdown("**Результат с unsafe_allow_html=True:**")
    st.markdown(problem_html, unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("🔍 Тест 3: Проверка условия")
    has_table = '<table' in problem_html and '</table>' in problem_html
    st.write(f"Содержит ли контент HTML таблицу? **{has_table}**")
    
    if has_table:
        st.success("✅ Условие выполняется - должен использоваться unsafe_allow_html=True")
    else:
        st.error("❌ Условие не выполняется - проблема в логике")
    
    st.divider()
    
    st.subheader("💬 Тест 4: В чате")
    st.markdown("**Как это выглядит в чате:**")
    
    with st.chat_message("assistant"):
        # Точно такая же логика как в app.py
        if '<table' in problem_html and '</table>' in problem_html:
            st.markdown(problem_html, unsafe_allow_html=True)
        else:
            st.markdown(problem_html)
    
    st.divider()
    
    st.subheader("🔧 Тест 5: Информация о браузере")
    st.markdown("""
    **Возможные причины проблемы:**
    
    1. **Кеш браузера** - попробуйте Ctrl+F5
    2. **Блокировщик рекламы** - может блокировать HTML
    3. **Настройки безопасности** браузера
    4. **Версия Streamlit** - проверьте версию
    """)
    
    # Информация о Streamlit
    st.info(f"**Версия Streamlit:** {st.__version__}")
    
    st.subheader("📋 Инструкции по исправлению")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Если таблица НЕ отображается:**
        
        1. Обновите страницу (Ctrl+F5)
        2. Очистите кеш браузера
        3. Попробуйте другой браузер
        4. Отключите блокировщики рекламы
        5. Попробуйте режим инкогнито
        """)
    
    with col2:
        st.markdown("""
        **Если таблица отображается:**
        
        1. Проблема в основном приложении
        2. Нужно проверить кеш Streamlit
        3. Возможно, нужен полный перезапуск
        4. Проверить версию Streamlit
        """)
    
    if st.button("🔄 Очистить кеш Streamlit"):
        st.cache_data.clear()
        if hasattr(st, 'cache_resource'):
            st.cache_resource.clear()
        st.success("✅ Кеш очищен!")
        st.rerun()

if __name__ == "__main__":
    main()