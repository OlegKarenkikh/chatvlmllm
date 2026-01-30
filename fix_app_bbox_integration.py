#!/usr/bin/env python3
"""
Исправление интеграции BBOX в app.py
"""

def create_bbox_fix():
    """Создание исправления для app.py"""
    
    fix_code = '''
# ИСПРАВЛЕНИЕ 1: Улучшенная функция отображения BBOX
def display_bbox_visualization_improved(ocr_result):
    """Улучшенная функция отображения BBOX визуализации"""
    
    if not ocr_result:
        return
    
    prompt_info = ocr_result.get("prompt_info", {})
    
    # Проверяем, включена ли визуализация BBOX
    if not prompt_info.get("bbox_enabled", False):
        return
    
    try:
        from utils.bbox_visualizer import BBoxVisualizer
        
        # Получаем данные
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
        
        # Обрабатываем ответ
        image_with_boxes, legend_img, elements = visualizer.process_dots_ocr_response(
            image, 
            response_text,
            show_labels=True,
            create_legend_img=True
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
        
        # Дополнительная информация об элементах
        with st.expander("🔍 Подробная информация об элементах"):
            for i, element in enumerate(elements):
                bbox = element['bbox']
                category = element.get('category', 'Unknown')
                text = element.get('text', '')
                
                # Ограничиваем длину текста для отображения
                display_text = text[:100] + "..." if len(text) > 100 else text
                
                st.write(f"**#{i+1}:** [{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}] - {category}")
                if display_text:
                    st.caption(f"Текст: {display_text}")
    
    except Exception as e:
        st.error(f"❌ Ошибка визуализации BBOX: {e}")
        
        # Отладочная информация
        with st.expander("🔧 Отладочная информация"):
            import traceback
            st.code(traceback.format_exc())
            
            if 'image' in locals():
                st.write(f"**Тип изображения:** {type(image)}")
                if hasattr(image, 'size'):
                    st.write(f"**Размер изображения:** {image.size}")
            
            if 'response_text' in locals():
                st.write(f"**Длина ответа:** {len(response_text)}")
                st.write(f"**Первые 200 символов:**")
                st.code(response_text[:200])

# ИСПРАВЛЕНИЕ 2: Замена в коде отображения сообщений
# Найдите в app.py код около строки 1180 и замените:

# СТАРЫЙ КОД:
# if prompt_info.get("bbox_enabled", False):
#     try:
#         from utils.bbox_visualizer import BBoxVisualizer
#         
#         visualizer = BBoxVisualizer()
#         image_with_boxes, legend_img, elements = visualizer.process_dots_ocr_response(
#             ocr_result["image"], 
#             ocr_result["text"],
#             show_labels=True,
#             create_legend_img=True
#         )
#         
#         if elements:
#             st.divider()
#             st.subheader("🔍 Визуализация обнаруженных элементов")
#             
#             col1, col2 = st.columns([2, 1])
#             
#             with col1:
#                 st.image(image_with_boxes, caption="Изображение с BBOX", use_container_width=True)
#             
#             with col2:
#                 if legend_img:
#                     st.image(legend_img, caption="Легенда", use_container_width=True)
#                 
#                 # Статистика
#                 stats = visualizer.get_statistics(elements)
#                 st.metric("Всего элементов", stats.get('total_elements', 0))
#                 st.metric("Категорий", stats.get('unique_categories', 0))
#                 
#                 # Детали по категориям
#                 with st.expander("📊 Детали по категориям"):
#                     for category, count in stats.get('categories', {}).items():
#                         st.write(f"**{category}:** {count}")
#     
#     except Exception as e:
#         st.error(f"Ошибка визуализации BBOX: {e}")

# НОВЫЙ КОД:
# display_bbox_visualization_improved(ocr_result)

# ИСПРАВЛЕНИЕ 3: Добавить функцию в начало файла app.py (после импортов)
'''

    return fix_code

def apply_fix_to_app():
    """Применение исправления к app.py"""
    
    print("🔧 ПРИМЕНЕНИЕ ИСПРАВЛЕНИЯ BBOX В APP.PY")
    print("=" * 50)
    
    # Читаем текущий app.py
    with open("app.py", "r", encoding="utf-8") as f:
        app_content = f.read()
    
    # Создаем улучшенную функцию
    improved_function = '''
def display_bbox_visualization_improved(ocr_result):
    """Улучшенная функция отображения BBOX визуализации"""
    
    if not ocr_result:
        return
    
    prompt_info = ocr_result.get("prompt_info", {})
    
    # Проверяем, включена ли визуализация BBOX
    if not prompt_info.get("bbox_enabled", False):
        return
    
    try:
        from utils.bbox_visualizer import BBoxVisualizer
        
        # Получаем данные
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
        
        # Обрабатываем ответ
        image_with_boxes, legend_img, elements = visualizer.process_dots_ocr_response(
            image, 
            response_text,
            show_labels=True,
            create_legend_img=True
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
        
        # Дополнительная информация об элементах
        with st.expander("🔍 Подробная информация об элементах"):
            for i, element in enumerate(elements):
                bbox = element['bbox']
                category = element.get('category', 'Unknown')
                text = element.get('text', '')
                
                # Ограничиваем длину текста для отображения
                display_text = text[:100] + "..." if len(text) > 100 else text
                
                st.write(f"**#{i+1}:** [{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}] - {category}")
                if display_text:
                    st.caption(f"Текст: {display_text}")
    
    except Exception as e:
        st.error(f"❌ Ошибка визуализации BBOX: {e}")
        
        # Отладочная информация
        with st.expander("🔧 Отладочная информация"):
            import traceback
            st.code(traceback.format_exc())
            
            if 'image' in locals():
                st.write(f"**Тип изображения:** {type(image)}")
                if hasattr(image, 'size'):
                    st.write(f"**Размер изображения:** {image.size}")
            
            if 'response_text' in locals():
                st.write(f"**Длина ответа:** {len(response_text)}")
                st.write(f"**Первые 200 символов:**")
                st.code(response_text[:200])

'''
    
    # Находим место для вставки функции (после импортов)
    import_end = app_content.find("# Page configuration")
    if import_end == -1:
        import_end = app_content.find("st.set_page_config")
    
    if import_end != -1:
        # Вставляем функцию
        new_content = app_content[:import_end] + improved_function + "\n\n" + app_content[import_end:]
        
        # Заменяем старый код BBOX на новый
        old_bbox_code = '''# Обработка BBOX если включена
                            if prompt_info.get("bbox_enabled", False):
                                try:
                                    from utils.bbox_visualizer import BBoxVisualizer
                                    
                                    visualizer = BBoxVisualizer()
                                    image_with_boxes, legend_img, elements = visualizer.process_dots_ocr_response(
                                        ocr_result["image"], 
                                        ocr_result["text"],
                                        show_labels=True,
                                        create_legend_img=True
                                    )
                                    
                                    if elements:
                                        st.divider()
                                        st.subheader("🔍 Визуализация обнаруженных элементов")
                                        
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
                                
                                except Exception as e:
                                    st.error(f"Ошибка визуализации BBOX: {e}")'''
        
        new_bbox_code = '''# Обработка BBOX если включена
                            display_bbox_visualization_improved(ocr_result)'''
        
        # Заменяем код
        new_content = new_content.replace(old_bbox_code, new_bbox_code)
        
        # Сохраняем исправленный файл
        with open("app_bbox_fixed.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("✅ Исправление создано: app_bbox_fixed.py")
        print("\n📋 Что исправлено:")
        print("   1. Добавлена улучшенная функция display_bbox_visualization_improved()")
        print("   2. Улучшена обработка ошибок и отладка")
        print("   3. Добавлены проверки наличия данных")
        print("   4. Улучшено отображение информации об элементах")
        
        print("\n🔄 Для применения исправления:")
        print("   1. Остановите Streamlit приложение")
        print("   2. Замените app.py на app_bbox_fixed.py:")
        print("      copy app_bbox_fixed.py app.py")
        print("   3. Запустите приложение заново")
        
        return True
    else:
        print("❌ Не удалось найти место для вставки функции")
        return False

def main():
    """Главная функция"""
    
    print("🔧 ИСПРАВЛЕНИЕ ИНТЕГРАЦИИ BBOX В STREAMLIT")
    print("=" * 50)
    
    # Показываем код исправления
    fix_code = create_bbox_fix()
    print("\n📝 КОД ИСПРАВЛЕНИЯ:")
    print(fix_code)
    
    # Применяем исправление
    print("\n" + "=" * 50)
    success = apply_fix_to_app()
    
    if success:
        print("\n✅ ИСПРАВЛЕНИЕ ГОТОВО!")
        print("💡 Теперь BBOX должны отображаться корректно в Streamlit интерфейсе")
    else:
        print("\n❌ ОШИБКА ПРИМЕНЕНИЯ ИСПРАВЛЕНИЯ")
        print("💡 Примените исправления вручную, используя код выше")

if __name__ == "__main__":
    main()