#!/usr/bin/env python3
"""
Тест HTML рендеринга прямо в основном приложении
"""

import streamlit as st

def test_html_rendering():
    """Тестирование HTML рендеринга"""
    
    st.title("🧪 Тест HTML рендеринга в приложении")
    
    # Простой HTML
    simple_html = "<p style='color: red; font-weight: bold;'>Это красный жирный текст</p>"
    
    st.subheader("Тест 1: Простой HTML")
    st.markdown("**Исходный код:**")
    st.code(simple_html, language="html")
    st.markdown("**Результат:**")
    st.markdown(simple_html, unsafe_allow_html=True)
    
    # HTML таблица
    table_html = """
    <table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">
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
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">2</td>
                <td style="border: 1px solid #ddd; padding: 8px;">Section-header</td>
                <td style="border: 1px solid #ddd; padding: 8px;">[309, 52, 873, 103]</td>
            </tr>
        </tbody>
    </table>
    """
    
    st.subheader("Тест 2: HTML таблица")
    st.markdown("**Исходный код:**")
    with st.expander("Показать HTML код"):
        st.code(table_html, language="html")
    st.markdown("**Результат:**")
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Тест BBoxTableRenderer
    st.subheader("Тест 3: BBoxTableRenderer")
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from utils.bbox_table_renderer import BBoxTableRenderer
        
        test_elements = [
            {"bbox": [81, 28, 220, 114], "category": "Picture", "text": ""},
            {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
            {"bbox": [309, 103, 873, 154], "category": "Section-header", "text": "РОССИЙСКАЯ ФЕДЕРАЦИЯ"}
        ]
        
        renderer = BBoxTableRenderer()
        generated_html = renderer.render_elements_table(test_elements)
        
        st.markdown("**Сгенерированный HTML (первые 300 символов):**")
        st.code(generated_html[:300] + "...", language="html")
        
        st.markdown("**Результат:**")
        st.markdown(generated_html, unsafe_allow_html=True)
        
        st.success("✅ BBoxTableRenderer работает!")
        
    except Exception as e:
        st.error(f"❌ Ошибка BBoxTableRenderer: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    test_html_rendering()