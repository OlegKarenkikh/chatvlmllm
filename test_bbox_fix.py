#!/usr/bin/env python3
"""
Тест исправления BBOX функциональности
"""

import streamlit as st
from PIL import Image
import json

def test_bbox_functionality():
    """Тестирование BBOX функциональности"""
    
    st.title("🔧 Тест BBOX функциональности")
    
    # Создаем тестовые данные
    test_image = Image.new('RGB', (800, 600), color='white')
    
    # Тестовые BBOX данные (как от dots.ocr)
    test_response = '''[
    {"bbox": [81, 28, 220, 114], "category": "Picture", "text": ""},
    {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
    {"bbox": [309, 103, 873, 154], "category": "Section-header", "text": "РОССИЙСКАЯ ФЕДЕРАЦИЯ"},
    {"bbox": [81, 154, 220, 205], "category": "Text", "text": "1. ИВАНОВ"},
    {"bbox": [81, 205, 220, 256], "category": "Text", "text": "2. ИВАН"},
    {"bbox": [81, 256, 220, 307], "category": "Text", "text": "3. ИВАНОВИЧ"},
    {"bbox": [309, 154, 450, 205], "category": "Text", "text": "4a) 01.01.1990"},
    {"bbox": [450, 154, 591, 205], "category": "Text", "text": "4b) МОСКВА"},
    {"bbox": [309, 205, 450, 256], "category": "Text", "text": "5. 1234567890"},
    {"bbox": [450, 205, 591, 256], "category": "Text", "text": "9. AA 123456"},
    {"bbox": [309, 256, 450, 307], "category": "Text", "text": "10. 01.01.2020"},
    {"bbox": [450, 256, 591, 307], "category": "Text", "text": "11. 01.01.2030"},
    {"bbox": [81, 307, 220, 358], "category": "Text", "text": "12. ГИБДД 7700"},
    {"bbox": [309, 307, 591, 358], "category": "Table", "text": "B, C, D"}
]'''
    
    # Создаем тестовый OCR результат
    test_ocr_result = {
        "text": test_response,
        "image": test_image,
        "prompt_info": {
            "bbox_enabled": True,
            "prompt": "Тестовый промпт с BBOX"
        }
    }
    
    st.info("🧪 Тестируем BBOX функциональность с тестовыми данными")
    
    # Импортируем функцию из app.py
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Импортируем функцию
        from app import display_bbox_visualization_improved
        
        st.success("✅ Функция display_bbox_visualization_improved импортирована")
        
        # Тестируем функцию
        st.subheader("🔍 Результат тестирования")
        display_bbox_visualization_improved(test_ocr_result)
        
    except Exception as e:
        st.error(f"❌ Ошибка при тестировании: {e}")
        
        # Отладочная информация
        with st.expander("🔧 Отладочная информация"):
            import traceback
            st.code(traceback.format_exc())
    
    # Дополнительная информация
    st.divider()
    st.subheader("📋 Информация о тесте")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Тестовые данные:**
        - 14 BBOX элементов
        - 6 различных категорий
        - Размер изображения: 800x600
        - Формат данных: JSON массив
        """)
    
    with col2:
        st.markdown("""
        **Ожидаемый результат:**
        - Изображение с цветными рамками
        - Легенда с категориями
        - Статистика элементов
        - Детальная таблица
        """)
    
    # Показываем сырые данные
    with st.expander("📄 Сырые тестовые данные"):
        st.code(test_response, language="json")

if __name__ == "__main__":
    test_bbox_functionality()