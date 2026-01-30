# [Исправленная версия app.py - только критические изменения]

# В разделе "📄 Режим OCR" после строки 740 (после st.session_state.ocr_result = {...})
# ДОБАВИТЬ:

# Сохраняем результат также для BBOX визуализации
if 'prompt_info' not in st.session_state.ocr_result:
    st.session_state.ocr_result['prompt_info'] = {
        'bbox_enabled': True,  # Всегда включаем BBOX для OCR режима
        'table_processing': document_type in ['invoice', 'table']
    }
    st.session_state.ocr_result['image'] = processed_image

# Копируем в last_ocr_result для display_bbox_visualization_improved
st.session_state.last_ocr_result = st.session_state.ocr_result.copy()

st.success("✅ Текст успешно извлечен!")

# ДОБАВИТЬ визуализацию BBOX сразу после извлечения
if result.get('text'):
    # Проверяем наличие JSON с BBOX
    if is_dots_ocr_json_response(result['text']):
        st.info("🔍 Обнаружен JSON с BBOX координатами")
        display_bbox_visualization_improved(st.session_state.last_ocr_result)

st.rerun()


# В разделе отображения результатов OCR (около строки 770)
# ЗАМЕНИТЬ блок отображения текста:

# Extracted text
st.markdown("**🔤 Распознанный текст:**")

# ПРАВИЛЬНАЯ ОБРАБОТКА JSON И HTML ТАБЛИЦ
if is_dots_ocr_json_response(result["text"]):
    # Конвертируем JSON в HTML таблицу
    html_table = convert_dots_ocr_json_to_html_table(result["text"])
    st.markdown("📊 **Результаты распознавания (таблица):**")
    st.markdown(html_table, unsafe_allow_html=True)
    st.success("✅ JSON автоматически преобразован в таблицу")
    
    # Показываем оригинальный JSON в свернутом виде
    with st.expander("🔍 Посмотреть оригинальный JSON"):
        st.code(result["text"], language="json")
else:
    # Обычный текст
    st.code(result["text"], language="text")

st.divider()

# ДОБАВИТЬ визуализацию BBOX если есть
if hasattr(st.session_state, 'last_ocr_result'):
    display_bbox_visualization_improved(st.session_state.last_ocr_result)


# ИНСТРУКЦИИ ПО ПРИМЕНЕНИЮ ИСПРАВЛЕНИЙ:
# 1. Найти в app.py строку с st.session_state.ocr_result = {...}
# 2. Добавить после неё код для сохранения в last_ocr_result
# 3. Найти блок отображения распознанного текста
# 4. Заменить st.code(result["text"]) на проверку is_dots_ocr_json_response
# 5. Добавить вызов display_bbox_visualization_improved после отображения текста