#!/usr/bin/env python3
"""
Исправление интеграции BBOX визуализации в Streamlit
"""

import streamlit as st
import json
from PIL import Image
from utils.bbox_visualizer import BBoxVisualizer

def test_streamlit_bbox_integration():
    """Тестирование интеграции BBOX в Streamlit"""
    
    st.title("🔍 Тест BBOX визуализации")
    
    # Загружаем тестовые данные
    sample_bbox_data = [
        {"bbox": [81, 28, 220, 114], "category": "Picture"},
        {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
        {"bbox": [45, 147, 284, 489], "category": "Picture"},
        {"bbox": [334, 129, 575, 180], "category": "List-item", "text": "1. ВАКАРИНЦЕВ\n VAKARINTSEV"},
        {"bbox": [332, 184, 664, 237], "category": "List-item", "text": "2. АНДРЕЙ ПАВЛОВИЧ\n ANDREY PAVLOVICH"},
        {"bbox": [332, 241, 636, 325], "category": "List-item", "text": "3. 13.09.1995\n АЛТАЙСКИЙ КРАЙ\n ALTAYSKIY KRAY"},
        {"bbox": [332, 328, 521, 360], "category": "List-item", "text": "4а) 03.01.2014"},
        {"bbox": [583, 328, 770, 362], "category": "List-item", "text": "4b) 03.01.2020"},
        {"bbox": [332, 362, 544, 412], "category": "List-item", "text": "4с) ГИБДД 2247\n GIBDD 2247"},
        {"bbox": [330, 416, 548, 448], "category": "List-item", "text": "5. 22 13 616660"},
        {"bbox": [329, 450, 635, 503], "category": "List-item", "text": "8. АЛТАЙСКИЙ КРАЙ\n ALTAYSKIY KRAY"},
        {"bbox": [329, 517, 417, 559], "category": "List-item", "text": "9. B"},
        {"bbox": [34, 501, 60, 528], "category": "Text", "text": "6."},
        {"bbox": [33, 537, 247, 610], "category": "Picture"}
    ]
    
    # Создаем тестовое изображение
    if st.button("🎯 Создать тест BBOX"):
        
        # Определяем размер изображения на основе координат
        max_x = max(max(item['bbox'][0], item['bbox'][2]) for item in sample_bbox_data)
        max_y = max(max(item['bbox'][1], item['bbox'][3]) for item in sample_bbox_data)
        
        # Создаем изображение с отступами
        img_width = max_x + 100
        img_height = max_y + 100
        
        st.info(f"📏 Размер изображения: {img_width}x{img_height}")
        
        # Создаем белое изображение
        test_image = Image.new('RGB', (img_width, img_height), 'white')
        
        # Инициализируем визуализатор
        visualizer = BBoxVisualizer()
        
        # Конвертируем данные в JSON
        json_response = json.dumps(sample_bbox_data, ensure_ascii=False, indent=2)
        
        try:
            # Обрабатываем ответ
            image_with_boxes, legend_img, elements = visualizer.process_dots_ocr_response(
                test_image, 
                json_response,
                show_labels=True,
                create_legend_img=True
            )
            
            st.success(f"✅ Обработано {len(elements)} элементов")
            
            # Отображаем результаты
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🖼️ Изображение с BBOX")
                st.image(image_with_boxes, caption="Визуализация BBOX", use_container_width=True)
            
            with col2:
                if legend_img:
                    st.subheader("🏷️ Легенда")
                    st.image(legend_img, caption="Категории элементов", use_container_width=True)
                
                # Статистика
                stats = visualizer.get_statistics(elements)
                st.subheader("📊 Статистика")
                st.metric("Всего элементов", stats.get('total_elements', 0))
                st.metric("Категорий", stats.get('unique_categories', 0))
                
                # Детали по категориям
                with st.expander("📋 Детали по категориям"):
                    for category, count in stats.get('categories', {}).items():
                        st.write(f"**{category}:** {count}")
            
            # Детальная информация об элементах
            st.subheader("🔍 Детали элементов")
            
            for i, element in enumerate(elements):
                bbox = element['bbox']
                category = element.get('category', 'Unknown')
                text = element.get('text', '')
                
                with st.expander(f"#{i+1}: {category} - {bbox}"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Координаты:** [{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]")
                        st.write(f"**Размер:** {bbox[2]-bbox[0]}x{bbox[3]-bbox[1]}")
                        st.write(f"**Категория:** {category}")
                    
                    with col_b:
                        if text:
                            st.write(f"**Текст:**")
                            st.code(text, language=None)
                        else:
                            st.write("*Текст отсутствует*")
            
        except Exception as e:
            st.error(f"❌ Ошибка обработки: {e}")
            import traceback
            st.code(traceback.format_exc())

def improved_bbox_integration_for_app():
    """Улучшенная функция интеграции BBOX для основного приложения"""
    
    code = '''
def display_bbox_visualization(image, response_text, prompt_info):
    """Улучшенная функция отображения BBOX визуализации"""
    
    if not prompt_info.get("bbox_enabled", False):
        return
    
    try:
        from utils.bbox_visualizer import BBoxVisualizer
        
        # Проверяем, что у нас есть изображение
        if image is None:
            st.warning("⚠️ Изображение не найдено для визуализации BBOX")
            return
        
        # Проверяем размер изображения
        st.info(f"📏 Размер изображения: {image.size[0]}x{image.size[1]}")
        
        visualizer = BBoxVisualizer()
        
        # Обрабатываем ответ
        image_with_boxes, legend_img, elements = visualizer.process_dots_ocr_response(
            image, 
            response_text,
            show_labels=True,
            create_legend_img=True
        )
        
        if not elements:
            st.warning("⚠️ BBOX элементы не найдены в ответе модели")
            st.info("💡 Убедитесь, что используется промпт с поддержкой BBOX")
            return
        
        st.divider()
        st.subheader("🔍 Визуализация обнаруженных элементов")
        
        # Основное отображение
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(image_with_boxes, caption="Изображение с BBOX", use_container_width=True)
        
        with col2:
            if legend_img:
                st.image(legend_img, caption="Легенда", use_container_width=True)
            
            # Статистика
            stats = visualizer.get_statistics(elements)
            st.metric("Всего элементов", stats.get('total_elements', 0))
            st.metric("Категорий", stats.get('unique_categories', 0))
            
            # Детали по категориям
            with st.expander("📊 Детали по категориям"):
                for category, count in stats.get('categories', {}).items():
                    st.write(f"**{category}:** {count}")
        
        # Дополнительная информация
        with st.expander("🔍 Подробная информация об элементах"):
            for i, element in enumerate(elements):
                bbox = element['bbox']
                category = element.get('category', 'Unknown')
                text = element.get('text', '')[:100] + "..." if len(element.get('text', '')) > 100 else element.get('text', '')
                
                st.write(f"**#{i+1}:** [{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}] - {category}")
                if text:
                    st.caption(f"Текст: {text}")
    
    except Exception as e:
        st.error(f"❌ Ошибка визуализации BBOX: {e}")
        st.info("💡 Проверьте формат ответа модели и наличие BBOX координат")
        
        # Отладочная информация
        with st.expander("🔧 Отладочная информация"):
            st.write("**Тип изображения:**", type(image))
            st.write("**Размер ответа:**", len(response_text) if response_text else 0)
            st.write("**Первые 200 символов ответа:**")
            st.code(response_text[:200] if response_text else "Пустой ответ")
'''
    
    st.subheader("💻 Код для интеграции в app.py")
    st.code(code, language='python')
    
    st.info("""
    **Инструкции по интеграции:**
    
    1. Замените существующую функцию обработки BBOX в app.py на код выше
    2. Убедитесь, что передается правильное изображение (PIL.Image объект)
    3. Проверьте, что response_text содержит JSON с BBOX координатами
    4. Убедитесь, что prompt_info содержит bbox_enabled: True
    """)

def main():
    """Главная функция"""
    
    st.set_page_config(
        page_title="BBOX Integration Fix",
        page_icon="🔧",
        layout="wide"
    )
    
    tab1, tab2 = st.tabs(["🧪 Тест BBOX", "💻 Код интеграции"])
    
    with tab1:
        test_streamlit_bbox_integration()
    
    with tab2:
        improved_bbox_integration_for_app()

if __name__ == "__main__":
    main()