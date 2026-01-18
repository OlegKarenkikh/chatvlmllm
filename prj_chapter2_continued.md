## 2.4. Реализация веб-интерфейса на Streamlit

Веб-интерфейс разработан с использованием Streamlit для обеспечения интуитивного взаимодействия с системой без необходимости технических знаний.

**Главная страница и навигация:**
```python
import streamlit as st
from pathlib import Path
import yaml

def load_config():
    """Загрузка конфигурации системы"""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    st.set_page_config(
        page_title="ChatVLMLLM - Распознавание документов",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Боковая панель с навигацией
    with st.sidebar:
        st.title("🔬 ChatVLMLLM")
        st.markdown("Система распознавания документов")
        
        mode = st.selectbox(
            "Выберите режим работы:",
            ["OCR - Распознавание текста", 
             "Чат с документом", 
             "Извлечение полей",
             "Пакетная обработка"]
        )
        
        # Выбор модели
        config = load_config()
        available_models = list(config["models"].keys())
        selected_model = st.selectbox("Модель:", available_models)
```

**Интерфейс загрузки документов:**
```python
def document_upload_interface():
    """Интерфейс для загрузки документов"""
    st.header("📄 Загрузка документа")
    
    # Поддерживаемые форматы
    supported_formats = ["jpg", "jpeg", "png", "bmp", "tiff"]
    
    uploaded_file = st.file_uploader(
        "Выберите изображение документа",
        type=supported_formats,
        help="Поддерживаемые форматы: " + ", ".join(supported_formats.upper())
    )
    
    if uploaded_file is not None:
        # Отображение превью
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(uploaded_file, caption="Загруженный документ", width=300)
            
        with col2:
            # Информация о файле
            st.write("**Информация о файле:**")
            st.write(f"Название: {uploaded_file.name}")
            st.write(f"Размер: {uploaded_file.size / 1024:.1f} KB")
            st.write(f"Тип: {uploaded_file.type}")
            
        return uploaded_file
    return None
```

**Интерфейс обработки и результатов:**
```python
def processing_interface(uploaded_file, model_name, mode):
    """Интерфейс обработки документа"""
    if st.button("🚀 Начать обработку", type="primary"):
        with st.spinner("Обработка документа..."):
            # Прогресс-бар
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Загрузка модели
                status_text.text("Загрузка модели...")
                progress_bar.progress(20)
                
                model_manager = get_model_manager()
                model = model_manager.get_model(model_name)
                
                # Предобработка изображения
                status_text.text("Предобработка изображения...")
                progress_bar.progress(40)
                
                image = Image.open(uploaded_file)
                processed_image = preprocess_image(image)
                
                # Обработка моделью
                status_text.text("Распознавание документа...")
                progress_bar.progress(70)
                
                result = model.process_image(processed_image, mode)
                
                # Постобработка результатов
                status_text.text("Постобработка результатов...")
                progress_bar.progress(90)
                
                cleaned_result = clean_ocr_result(result["text"])
                
                progress_bar.progress(100)
                status_text.text("Обработка завершена!")
                
                # Отображение результатов
                display_results(cleaned_result, result)
                
            except Exception as e:
                st.error(f"Ошибка при обработке: {str(e)}")
                st.exception(e)
```

**Отображение результатов:**
```python
def display_results(text_result, full_result):
    """Отображение результатов обработки"""
    st.header("📊 Результаты обработки")
    
    # Вкладки для различных представлений результатов
    tab1, tab2, tab3, tab4 = st.tabs(["Текст", "Поля", "Метрики", "Экспорт"])
    
    with tab1:
        st.subheader("Распознанный текст")
        st.text_area("", value=text_result, height=300, disabled=True)
        
    with tab2:
        st.subheader("Извлеченные поля")
        if "fields" in full_result:
            for field, value in full_result["fields"].items():
                st.write(f"**{field}:** {value}")
        else:
            st.info("Структурированные поля не извлечены")
            
    with tab3:
        st.subheader("Метрики качества")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            confidence = full_result.get("confidence", 0.85)
            st.metric("Уверенность", f"{confidence:.1%}")
            
        with col2:
            processing_time = full_result.get("processing_time", 0)
            st.metric("Время обработки", f"{processing_time:.1f}с")
            
        with col3:
            char_count = len(text_result)
            st.metric("Символов", char_count)
            
    with tab4:
        st.subheader("Экспорт результатов")
        export_format = st.selectbox("Формат:", ["JSON", "CSV", "TXT"])
        
        if st.button("Скачать результаты"):
            export_data = prepare_export_data(full_result, export_format)
            st.download_button(
                label=f"Скачать {export_format}",
                data=export_data,
                file_name=f"ocr_results.{export_format.lower()}",
                mime=get_mime_type(export_format)
            )
```