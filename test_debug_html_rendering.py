#!/usr/bin/env python3
"""
Тест с отладочной информацией для HTML рендеринга
"""

import streamlit as st
import sys
import importlib

# Принудительная перезагрузка модулей
if 'utils.smart_content_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.smart_content_renderer'])
if 'utils.html_table_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.html_table_renderer'])

from utils.smart_content_renderer import SmartContentRenderer

def main():
    st.title("🔧 Отладка HTML рендеринга")
    
    # Тестовый контент
    test_content = """📋 Детальная информация<table class="bbox-table">         <thead>             <tr>                 <th style="width: 50px;">#</th>                 <th style="width: 150px;">Категория</th>                 <th style="width: 200px;">BBOX координаты</th>                 <th>Текст</th>             </tr>         </thead>         <tbody>             <tr>                 <td>1</td>                 <td>Заголовок документа</td>                 <td>[45, 123, 567, 189]</td>                 <td>ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ</td>             </tr>         </tbody>     </table>

Анализ завершен."""
    
    st.subheader("🧪 Тест SmartContentRenderer с отладкой")
    st.write("Проверьте консоль/терминал для отладочной информации")
    
    if st.button("🚀 Запустить тест"):
        st.write("**Результат рендеринга:**")
        try:
            SmartContentRenderer.render_content_smart(test_content)
            st.success("✅ Рендеринг завершен (проверьте консоль)")
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")
            st.exception(e)
    
    st.divider()
    
    # Показываем исходный контент
    with st.expander("Показать исходный контент"):
        st.code(test_content)
    
    # Тест определения HTML
    st.subheader("🔍 Тест определения HTML")
    has_html = SmartContentRenderer.has_html_content(test_content)
    st.write(f"HTML обнаружен: **{has_html}**")
    
    if has_html:
        content_info = SmartContentRenderer.extract_html_and_text(test_content)
        st.write(f"Найдено таблиц: **{len(content_info['tables'])}**")
        
        if content_info['tables']:
            with st.expander("Показать извлеченную таблицу"):
                st.code(content_info['tables'][0])

if __name__ == "__main__":
    main()