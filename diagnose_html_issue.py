#!/usr/bin/env python3
"""
Диагностика проблемы с HTML отображением
"""

import streamlit as st
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    st.set_page_config(
        page_title="HTML Issue Diagnosis",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Диагностика проблемы с HTML отображением")
    
    # Тестовые данные
    test_elements = [
        {"bbox": [81, 28, 220, 114], "category": "Picture", "text": ""},
        {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
        {"bbox": [309, 103, 873, 154], "category": "Section-header", "text": "РОССИЙСКАЯ ФЕДЕРАЦИЯ"}
    ]
    
    st.info(f"📊 Тестовые данные: {len(test_elements)} элементов")
    
    # Тест 1: Простой HTML
    st.subheader("🧪 Тест 1: Простой HTML")
    simple_html = "<p style='color: red; font-weight: bold;'>Это красный жирный текст</p>"
    
    st.markdown("**Исходный HTML:**")
    st.code(simple_html, language="html")
    
    st.markdown("**Результат отображения:**")
    st.markdown(simple_html, unsafe_allow_html=True)
    
    # Тест 2: HTML таблица
    st.subheader("🧪 Тест 2: HTML таблица")
    table_html = """
    <table style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr style="background-color: #4CAF50; color: white;">
                <th style="border: 1px solid #ddd; padding: 8px;">№</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Категория</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Координаты</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">1</td>
                <td style="border: 1px solid #ddd; padding: 8px;">Picture</td>
                <td style="border: 1px solid #ddd; padding: 8px;">[81, 28, 220, 114]</td>
            </tr>
        </tbody>
    </table>
    """
    
    st.markdown("**Исходный HTML:**")
    with st.expander("Показать HTML код"):
        st.code(table_html, language="html")
    
    st.markdown("**Результат отображения:**")
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Тест 3: BBoxTableRenderer
    st.subheader("🧪 Тест 3: BBoxTableRenderer")
    
    try:
        from utils.bbox_table_renderer import BBoxTableRenderer
        st.success("✅ BBoxTableRenderer импортирован")
        
        renderer = BBoxTableRenderer()
        
        # Генерируем HTML
        generated_html = renderer.render_elements_table(test_elements)
        
        st.markdown("**Сгенерированный HTML (первые 500 символов):**")
        st.code(generated_html[:500] + "...", language="html")
        
        st.markdown("**Результат отображения:**")
        st.markdown(generated_html, unsafe_allow_html=True)
        
        # Проверяем, что отображается
        if "<table" in generated_html and "</table>" in generated_html:
            st.success("✅ HTML содержит корректную таблицу")
        else:
            st.error("❌ HTML не содержит таблицу")
            
    except Exception as e:
        st.error(f"❌ Ошибка BBoxTableRenderer: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    # Тест 4: Проверка версии Streamlit
    st.subheader("🧪 Тест 4: Информация о системе")
    
    import streamlit as st_version
    st.write(f"**Версия Streamlit:** {st_version.__version__}")
    
    # Тест 5: Альтернативные способы отображения
    st.subheader("🧪 Тест 5: Альтернативные способы")
    
    # Способ 1: st.html (если доступен)
    try:
        st.markdown("**Способ 1: st.html**")
        if hasattr(st, 'html'):
            st.html(simple_html)
            st.success("✅ st.html работает")
        else:
            st.warning("⚠️ st.html недоступен")
    except Exception as e:
        st.error(f"❌ st.html ошибка: {e}")
    
    # Способ 2: st.components.v1.html
    try:
        st.markdown("**Способ 2: st.components.v1.html**")
        import streamlit.components.v1 as components
        components.html(f"<div>{simple_html}</div>", height=100)
        st.success("✅ components.html работает")
    except Exception as e:
        st.error(f"❌ components.html ошибка: {e}")
    
    # Диагностика проблемы
    st.divider()
    st.subheader("🔍 Диагностика")
    
    st.markdown("""
    **Если вы видите HTML код вместо отформатированного содержимого:**
    
    1. **Проверьте версию Streamlit** - возможно, нужно обновление
    2. **Очистите кэш браузера** - нажмите Ctrl+F5
    3. **Проверьте настройки безопасности** - некоторые браузеры блокируют HTML
    4. **Попробуйте другой браузер** - Chrome, Firefox, Edge
    
    **Если простой HTML работает, а таблица нет:**
    - Проблема в сложности HTML или CSS стилях
    - Streamlit может блокировать некоторые CSS свойства
    
    **Если ничего не работает:**
    - Проблема в настройках Streamlit или браузера
    - Нужно использовать альтернативные методы отображения
    """)

if __name__ == "__main__":
    main()