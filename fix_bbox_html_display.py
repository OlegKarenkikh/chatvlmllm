#!/usr/bin/env python3
"""
Исправление отображения HTML в детальной информации BBOX
"""

import streamlit as st
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bbox_html_rendering():
    """Тестирование HTML рендеринга BBOX таблицы"""
    
    st.title("🔧 Тест HTML рендеринга BBOX таблицы")
    
    # Тестовые данные
    test_elements = [
        {"bbox": [81, 28, 220, 114], "category": "Picture", "text": ""},
        {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
        {"bbox": [309, 103, 873, 154], "category": "Section-header", "text": "РОССИЙСКАЯ ФЕДЕРАЦИЯ"},
        {"bbox": [81, 154, 220, 205], "category": "Text", "text": "1. ИВАНОВ"},
        {"bbox": [81, 205, 220, 256], "category": "Text", "text": "2. ИВАН"}
    ]
    
    st.info(f"📊 Тестовые данные: {len(test_elements)} элементов")
    
    try:
        from utils.bbox_table_renderer import BBoxTableRenderer
        st.success("✅ BBoxTableRenderer импортирован успешно")
        
        renderer = BBoxTableRenderer()
        
        # Тестируем статистику
        st.subheader("📊 Статистика")
        stats_html = renderer.render_statistics(test_elements)
        st.markdown(stats_html, unsafe_allow_html=True)
        
        # Тестируем легенду
        st.subheader("🎨 Легенда")
        legend_html = renderer.render_legend(test_elements)
        st.markdown(legend_html, unsafe_allow_html=True)
        
        # Тестируем детальную таблицу
        st.subheader("📋 Детальная информация")
        table_html = renderer.render_elements_table(test_elements)
        
        # Показываем HTML код для отладки
        with st.expander("🔧 HTML код (для отладки)"):
            st.code(table_html[:500] + "..." if len(table_html) > 500 else table_html, language="html")
        
        # Отображаем таблицу
        st.markdown(table_html, unsafe_allow_html=True)
        
        st.success("✅ HTML таблица отображена успешно!")
        
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        import traceback
        st.code(traceback.format_exc())

def fix_app_bbox_html_display():
    """Исправление отображения HTML в app.py"""
    
    st.title("🔧 Исправление HTML отображения в app.py")
    
    # Читаем текущий app.py
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        st.success("✅ Файл app.py прочитан")
        
        # Ищем проблемный участок
        if 'st.markdown(table_renderer.render_elements_table(elements), unsafe_allow_html=True)' in content:
            st.info("✅ Найден код HTML рендеринга таблицы")
        else:
            st.warning("⚠️ Код HTML рендеринга не найден")
        
        # Улучшенная функция отображения BBOX
        improved_bbox_display = '''
def display_bbox_visualization_improved(ocr_result):
    """Улучшенная функция отображения BBOX визуализации с исправленным HTML рендерингом"""
    
    if not ocr_result:
        return
    
    prompt_info = ocr_result.get("prompt_info", {})
    
    # Проверяем, включена ли визуализация BBOX
    if not prompt_info.get("bbox_enabled", False):
        return
    
    try:
        from utils.bbox_visualizer import BBoxVisualizer
        from utils.bbox_table_renderer import BBoxTableRenderer
        
        # Получаем данные с проверками
        image = ocr_result.get("image")
        response_text = ocr_result.get("text", "")
        
        # Проверяем наличие изображения
        if image is None:
            st.warning("⚠️ Изображение не найдено для визуализации BBOX")
            return
        
        # Отладочная информация
        st.info(f"📏 Размер изображения: {image.size[0]}x{image.size[1]}")
        
        # Инициализируем визуализатор
        visualizer = BBoxVisualizer()
        table_renderer = BBoxTableRenderer()
        
        # Обрабатываем ответ
        image_with_boxes, legend_img, elements = visualizer.process_dots_ocr_response(
            image, response_text, show_labels=True, create_legend_img=True
        )
        
        if not elements:
            st.warning("⚠️ BBOX элементы не найдены в ответе модели")
            st.info("💡 Убедитесь, что модель вернула JSON с BBOX координатами")
            
            # Показываем первые 300 символов ответа для отладки
            with st.expander("🔧 Отладка ответа модели"):
                st.code(response_text[:300] + "..." if len(response_text) > 300 else response_text)
            return
        
        # Отображаем результаты
        st.divider()
        st.subheader("🔍 Визуализация обнаруженных элементов")
        
        # HTML статистика и легенда
        try:
            st.markdown(table_renderer.render_statistics(elements), unsafe_allow_html=True)
            st.markdown(table_renderer.render_legend(elements), unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"⚠️ Не удалось отобразить HTML статистику: {e}")
        
        # Основное отображение
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(image_with_boxes, caption="Изображение с BBOX", use_container_width=True)
        
        with col2:
            if legend_img:
                st.image(legend_img, caption="Легенда", use_container_width=True)
            
            # Статистика (fallback)
            stats = visualizer.get_statistics(elements)
            st.metric("Всего элементов", stats.get('total_elements', 0))
            st.metric("Категорий", stats.get('unique_categories', 0))
        
        # ИСПРАВЛЕННОЕ отображение детальной информации
        st.subheader("📋 Детальная информация")
        
        try:
            # Пытаемся отобразить HTML таблицу
            table_html = table_renderer.render_elements_table(elements)
            st.markdown(table_html, unsafe_allow_html=True)
            st.success("✅ HTML таблица отображена")
            
        except Exception as e:
            st.warning(f"⚠️ HTML таблица не работает: {e}")
            
            # Fallback - красивое текстовое отображение
            st.markdown("**Элементы (текстовый формат):**")
            
            for i, element in enumerate(elements, 1):
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
    
    except Exception as e:
        st.error(f"❌ Ошибка визуализации BBOX: {e}")
        
        # Отладочная информация
        with st.expander("🔧 Отладочная информация"):
            import traceback
            st.code(traceback.format_exc())
'''
        
        st.code(improved_bbox_display, language="python")
        
        if st.button("🔧 Применить исправление"):
            # Заменяем функцию в app.py
            # Ищем существующую функцию display_bbox_visualization_improved
            import re
            
            # Паттерн для поиска функции
            pattern = r'def display_bbox_visualization_improved\(.*?\n(?:.*\n)*?(?=\ndef|\nclass|\n@|\nif __name__|\Z)'
            
            if re.search(pattern, content, re.MULTILINE):
                # Заменяем существующую функцию
                new_content = re.sub(pattern, improved_bbox_display.strip(), content, flags=re.MULTILINE)
                st.info("✅ Найдена существующая функция - заменяем")
            else:
                # Добавляем новую функцию
                # Ищем место для вставки (после импортов)
                import_end = content.find('\n\n# ')
                if import_end == -1:
                    import_end = content.find('\ndef ')
                
                if import_end != -1:
                    new_content = content[:import_end] + '\n\n' + improved_bbox_display + '\n' + content[import_end:]
                    st.info("✅ Добавляем новую функцию")
                else:
                    st.error("❌ Не удалось найти место для вставки функции")
                    return
            
            # Сохраняем исправленный файл
            try:
                with open("app_bbox_html_fixed.py", "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                st.success("✅ Исправленный файл сохранен как app_bbox_html_fixed.py")
                st.info("💡 Переименуйте app_bbox_html_fixed.py в app.py для применения исправлений")
                
            except Exception as e:
                st.error(f"❌ Ошибка сохранения: {e}")
    
    except Exception as e:
        st.error(f"❌ Ошибка чтения app.py: {e}")

def main():
    """Главная функция"""
    
    st.set_page_config(
        page_title="BBOX HTML Fix",
        page_icon="🔧",
        layout="wide"
    )
    
    tab1, tab2 = st.tabs(["🧪 Тест HTML", "🔧 Исправление"])
    
    with tab1:
        test_bbox_html_rendering()
    
    with tab2:
        fix_app_bbox_html_display()

if __name__ == "__main__":
    main()