#!/usr/bin/env python3
"""
Принудительное окончательное исправление HTML рендеринга
"""

import streamlit as st
import re

def main():
    st.title("🔧 Принудительное исправление HTML рендеринга")
    
    # Принудительная очистка кеша
    st.cache_data.clear()
    if hasattr(st, 'cache_resource'):
        st.cache_resource.clear()
    
    st.info("🔄 Кеш очищен. Тестируем HTML рендеринг...")
    
    # Тестовый HTML контент
    test_html = """📋 Детальная информация<table class="bbox-table" style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">
<thead>
<tr style="background-color: #4CAF50; color: white;">
<th style="border: 1px solid #ddd; padding: 10px; text-align: left;">#</th>
<th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Категория</th>
<th style="border: 1px solid #ddd; padding: 10px; text-align: left;">BBOX координаты</th>
<th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Текст</th>
</tr>
</thead>
<tbody>
<tr>
<td style="border: 1px solid #ddd; padding: 8px;">1</td>
<td style="border: 1px solid #ddd; padding: 8px;">Text</td>
<td style="border: 1px solid #ddd; padding: 8px;">[100, 200, 300, 250]</td>
<td style="border: 1px solid #ddd; padding: 8px;">Пример текста документа</td>
</tr>
<tr style="background-color: #f2f2f2;">
<td style="border: 1px solid #ddd; padding: 8px;">2</td>
<td style="border: 1px solid #ddd; padding: 8px;">Title</td>
<td style="border: 1px solid #ddd; padding: 8px;">[50, 50, 400, 100]</td>
<td style="border: 1px solid #ddd; padding: 8px;">Заголовок документа</td>
</tr>
<tr>
<td style="border: 1px solid #ddd; padding: 8px;">3</td>
<td style="border: 1px solid #ddd; padding: 8px;">Picture</td>
<td style="border: 1px solid #ddd; padding: 8px;">[200, 300, 500, 400]</td>
<td style="border: 1px solid #ddd; padding: 8px;">Изображение в документе</td>
</tr>
</tbody>
</table>

Анализ завершен успешно."""

    st.subheader("❌ Проблемный способ (как сейчас)")
    st.markdown("Обычный st.markdown() без unsafe_allow_html:")
    st.code(test_html[:200] + "...")
    
    st.subheader("✅ Правильный способ")
    st.markdown("С unsafe_allow_html=True:")
    
    # Принудительное отображение HTML
    st.markdown(test_html, unsafe_allow_html=True)
    
    st.subheader("💬 В чате должно быть так:")
    with st.chat_message("assistant"):
        st.markdown(test_html, unsafe_allow_html=True)
    
    st.success("✅ Если выше видна красивая таблица - исправление работает!")
    
    # Кнопка для принудительного исправления app.py
    if st.button("🚀 ПРИНУДИТЕЛЬНО ИСПРАВИТЬ APP.PY", type="primary"):
        force_fix_app()
        st.success("✅ Принудительное исправление применено!")
        st.info("🔄 Обновите страницу браузера (F5) и перезагрузите приложение")
        st.balloons()

def force_fix_app():
    """Принудительное исправление app.py"""
    
    # Читаем app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим и заменяем все вызовы display_message_with_html_support
    # на прямые вызовы st.markdown с unsafe_allow_html=True
    
    # Паттерн для замены
    old_pattern = r'display_message_with_html_support\(([^)]+)\)'
    
    # Новый код
    new_code = r'''# Принудительное отображение HTML
    if '<table' in \1 and '</table>' in \1:
        st.markdown(\1, unsafe_allow_html=True)
    else:
        st.markdown(\1)'''
    
    # Применяем замену
    content = re.sub(old_pattern, new_code, content)
    
    # Также добавляем принудительную очистку кеша в начало файла
    cache_clear = '''
# Принудительная очистка кеша для HTML рендеринга
import streamlit as st
if hasattr(st, 'cache_data'):
    st.cache_data.clear()
if hasattr(st, 'cache_resource'):
    st.cache_resource.clear()

'''
    
    # Вставляем очистку кеша после первого импорта
    first_import = content.find('import streamlit as st')
    if first_import != -1:
        import_end = content.find('\n', first_import) + 1
        content = content[:import_end] + cache_clear + content[import_end:]
    
    # Записываем обратно
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    main()