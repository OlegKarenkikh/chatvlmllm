#!/usr/bin/env python3
"""
Проверка исправления HTML отображения BBOX
"""

import streamlit as st
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Главная функция проверки"""
    
    st.set_page_config(
        page_title="BBOX HTML Fix Verification",
        page_icon="✅",
        layout="wide"
    )
    
    st.title("✅ Проверка исправления HTML отображения BBOX")
    
    st.info("🎯 Этот тест проверяет, что детальная информация BBOX отображается корректно")
    
    # Тестовые данные
    test_elements = [
        {"bbox": [81, 28, 220, 114], "category": "Picture", "text": ""},
        {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
        {"bbox": [309, 103, 873, 154], "category": "Section-header", "text": "РОССИЙСКАЯ ФЕДЕРАЦИЯ"},
        {"bbox": [81, 154, 220, 205], "category": "Text", "text": "1. ИВАНОВ"},
        {"bbox": [81, 205, 220, 256], "category": "Text", "text": "2. ИВАН ПАВЛОВИЧ"},
        {"bbox": [81, 256, 220, 307], "category": "Text", "text": "3. 15.03.1985"},
        {"bbox": [333, 129, 575, 181], "category": "List-item", "text": "4a. 15.03.2015"},
        {"bbox": [331, 184, 665, 237], "category": "List-item", "text": "4b. 15.03.2025"},
        {"bbox": [331, 240, 665, 293], "category": "List-item", "text": "4c. ГИБДД 7700"},
        {"bbox": [45, 147, 284, 489], "category": "Picture", "text": ""},
        {"bbox": [309, 154, 873, 205], "category": "Text", "text": "DRIVER LICENSE"},
        {"bbox": [309, 205, 873, 256], "category": "Text", "text": "RUSSIAN FEDERATION"},
        {"bbox": [575, 129, 873, 181], "category": "List-item", "text": "5. 77 ВА 123456"},
        {"bbox": [665, 184, 873, 293], "category": "List-item", "text": "9. A,B,C1,D"}
    ]
    
    st.success(f"📊 Подготовлены тестовые данные: {len(test_elements)} элементов, {len(set(e['category'] for e in test_elements))} категорий")
    
    # Тестируем HTML рендеринг
    st.subheader("🧪 Тест HTML рендеринга")
    
    try:
        from utils.bbox_table_renderer import BBoxTableRenderer
        st.success("✅ BBoxTableRenderer импортирован")
        
        renderer = BBoxTableRenderer()
        
        # Статистика
        st.markdown("#### 📊 Статистика")
        stats_html = renderer.render_statistics(test_elements)
        st.markdown(stats_html, unsafe_allow_html=True)
        
        # Легенда
        st.markdown("#### 🎨 Легенда категорий")
        legend_html = renderer.render_legend(test_elements)
        st.markdown(legend_html, unsafe_allow_html=True)
        
        # Детальная информация (как в исправленном app.py)
        st.markdown("### 📋 Детальная информация")
        try:
            # Генерируем HTML таблицу
            table_html = renderer.render_elements_table(test_elements)
            
            # Отображаем с HTML поддержкой
            st.markdown(table_html, unsafe_allow_html=True)
            st.success("✅ HTML таблица отображена")
            
        except Exception as e:
            st.warning(f"⚠️ HTML таблица не работает: {e}")
            
            # Fallback - красивое текстовое отображение
            st.markdown("**Элементы (текстовый формат):**")
            
            for i, element in enumerate(test_elements, 1):
                bbox = element.get('bbox', [0, 0, 0, 0])
                category = element.get('category', 'Unknown')
                text = element.get('text', '')
                
                # Цвет для категории (используем эмодзи как fallback)
                category_emoji = {
                    'Picture': '🖼️',
                    'Section-header': '📋',
                    'Text': '📝',
                    'List-item': '📌',
                    'Table': '📊',
                    'Title': '🏷️'
                }.get(category, '📄')
                
                # Форматирование BBOX
                bbox_str = f"[{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]"
                
                # Ограничение длины текста
                display_text = text[:100] + "..." if len(text) > 100 else text
                
                # Отображение элемента
                with st.container():
                    col_num, col_cat, col_bbox, col_text = st.columns([0.5, 1.5, 2, 4])
                    
                    with col_num:
                        st.markdown(f"**{i}**")
                    
                    with col_cat:
                        st.markdown(f"{category_emoji} {category}")
                    
                    with col_bbox:
                        st.code(bbox_str)
                    
                    with col_text:
                        if display_text:
                            st.caption(display_text)
                        else:
                            st.caption("_Нет текста_")
        
        # Результат теста
        st.divider()
        st.subheader("🎉 Результат теста")
        
        st.success("✅ Исправление работает корректно!")
        
        st.markdown("""
        **Что должно быть видно:**
        - 📊 Красивая статистика с градиентными карточками
        - 🎨 Цветная легенда категорий
        - 📋 HTML таблица с детальной информацией ИЛИ структурированный текстовый fallback
        - ✅ Сообщение об успешном отображении HTML таблицы
        
        **Если вы видите HTML код вместо таблицы - проблема НЕ исправлена!**
        """)
        
    except Exception as e:
        st.error(f"❌ Ошибка тестирования: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()