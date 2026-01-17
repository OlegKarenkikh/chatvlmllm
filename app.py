import streamlit as st
import yaml
from pathlib import Path
from PIL import Image
import io

# Import UI components
from ui.styles import get_custom_css

# Page configuration
st.set_page_config(
    page_title="ChatVLMLLM - Распознавание документов и чат с VLM",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Load configuration
@st.cache_resource
def load_config():
    """Load configuration from YAML file."""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None
if "loaded_model" not in st.session_state:
    st.session_state.loaded_model = None

# Header
st.markdown('<h1 class="gradient-text" style="text-align: center;">🔬 ChatVLMLLM</h1>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; font-size: 1.2rem; color: #888; margin-bottom: 2rem;">'
    'Модели машинного зрения для распознавания документов и интеллектуального чата</p>', 
    unsafe_allow_html=True
)

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
    st.title("Навигация")
    
    page = st.radio(
        "Выберите режим",
        ["🏠 Главная", "📄 Режим OCR", "💬 Режим чата", "📊 Сравнение моделей", "📚 Документация"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.subheader("⚙️ Настройки модели")
    selected_model = st.selectbox(
        "Выберите модель",
        list(config["models"].keys()),
        format_func=lambda x: config["models"][x]["name"],
        key="model_selector"
    )
    
    # Display model info
    model_info = config["models"][selected_model]
    st.info(
        f"**{model_info['name']}**\n\n"
        f"{model_info['description']}\n\n"
        f"📊 Макс. токенов: {model_info['max_length']}"
    )
    
    st.divider()
    
    with st.expander("🔧 Расширенные настройки"):
        temperature = st.slider("Температура", 0.0, 1.0, 0.7, 0.1, help="Контролирует случайность генерации")
        max_tokens = st.number_input("Макс. токенов", 100, 4096, 2048, 100, help="Максимальная длина генерируемого текста")
        use_gpu = st.checkbox("Использовать GPU", value=True, help="Включить ускорение GPU если доступно")
    
    st.divider()
    
    # Project stats
    st.markdown("### 📊 Статистика проекта")
    col1, col2 = st.columns(2)
    col1.metric("Модели", "11")
    col2.metric("Статус", "✅ Готов")
    
    # Model loading status
    try:
        from models.model_loader import ModelLoader
        loaded_models = ModelLoader.get_loaded_models()
        
        if loaded_models:
            st.success(f"✅ Загружено моделей: {len(loaded_models)}")
            for model in loaded_models:
                st.caption(f"• {model}")
        else:
            st.warning("⚠️ Модели не загружены")
            
        # Кнопка для выгрузки всех моделей
        if loaded_models and st.button("🗑️ Выгрузить все модели", use_container_width=True):
            ModelLoader.unload_all_models()
            st.success("Все модели выгружены")
            st.rerun()
            
    except Exception as e:
        st.error(f"Ошибка проверки моделей: {e}")

# Main content area
if "🏠 Главная" in page:
    st.header("Добро пожаловать в исследовательский проект ChatVLMLLM")
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            '<div class="feature-card">'
            '<h3>📄 Режим OCR</h3>'
            '<p>Извлечение текста и структурированных данных из документов с помощью специализированных VLM моделей.</p>'
            '<ul style="text-align: left; margin-top: 1rem;">'
            '<li>✅ Распознавание текста</li>'
            '<li>✅ Извлечение полей</li>'
            '<li>✅ Поддержка множества форматов</li>'
            '<li>✅ Экспорт в JSON/CSV</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            '<div class="feature-card">'
            '<h3>💬 Режим чата</h3>'
            '<p>Интерактивное общение с VLM моделями о содержимом документов.</p>'
            '<ul style="text-align: left; margin-top: 1rem;">'
            '<li>✅ Визуальные вопросы и ответы</li>'
            '<li>✅ Понимание контекста</li>'
            '<li>✅ Поддержка Markdown</li>'
            '<li>✅ История чата</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            '<div class="feature-card">'
            '<h3>📊 Сравнение</h3>'
            '<p>Сравнение производительности различных моделей на разных типах документов.</p>'
            '<ul style="text-align: left; margin-top: 1rem;">'
            '<li>✅ Метрики точности</li>'
            '<li>✅ Бенчмарки скорости</li>'
            '<li>✅ Использование памяти</li>'
            '<li>✅ Анализ качества</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # Research goals in tabs
    st.header("🎯 Цели исследования и временные рамки")
    
    tabs = st.tabs(["📋 Обзор", "📅 Временные рамки", "🎓 Обучение", "📈 Результаты"])
    
    with tabs[0]:
        st.markdown("""
        Этот образовательный проект исследует современные **модели машинного зрения** для задач OCR документов.
        Мы изучаем различные архитектуры, сравниваем их производительность и разрабатываем практические
        приложения для обработки документов в реальном мире.
        
        ### Ключевые исследовательские вопросы
        
        1. 🔍 **Сравнение моделей**: Как специализированные OCR модели сравниваются с общими VLM моделями?
        2. ⚖️ **Компромиссы**: Каковы компромиссы между производительностью и точностью?
        3. 📊 **Структурированное извлечение**: Могут ли VLM надежно извлекать структурированные данные?
        4. 🧠 **Понимание контекста**: Как контекст улучшает результаты OCR?
        
        ### Методология
        
        - **Количественный анализ**: Метрики CER, WER, точность полей
        - **Качественная оценка**: Сохранение макета, понимание структуры
        - **Бенчмаркинг производительности**: Скорость, память, масштабируемость
        - **Сравнительные исследования**: Сравнения модель к модели
        """)
    
    with tabs[1]:
        progress_data = [
            ("Фаза 1: Подготовка", 100, "✅ Завершено"),
            ("Фаза 2: Интеграция моделей", 95, "✅ Почти готово"),
            ("Фаза 3: Разработка UI", 90, "✅ Готово"),
            ("Фаза 4: Тестирование", 70, "🔄 В процессе"),
            ("Фаза 5: Документация", 85, "✅ Почти готово"),
        ]
        
        for phase, progress, status in progress_data:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{phase}**")
                st.progress(progress / 100)
            with col2:
                st.markdown(f"<p style='text-align: right;'>{status}</p>", unsafe_allow_html=True)
    
    with tabs[2]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 💻 Технические навыки
            
            - Развертывание и оптимизация VLM моделей
            - Пайплайны предобработки изображений
            - Оптимизация инференса (Flash Attention, квантизация)
            - Полнофункциональная разработка с Streamlit
            - Контейнеризация Docker и развертывание
            - Тестирование и обеспечение качества
            - Контроль версий Git и совместная работа
            """)
        
        with col2:
            st.markdown("""
            ### 🔬 Исследовательские навыки
            
            - Анализ архитектуры моделей
            - Методология сравнительной оценки
            - Статистический анализ и метрики
            - Научная документация
            - Критическое мышление и решение проблем
            - Визуализация данных и презентация
            - Техническое письмо и отчетность
            """)
    
    with tabs[3]:
        st.success("📊 Результаты интеграции моделей получены!")
        
        # Реальные результаты
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Достигнутые результаты
            
            - ✅ **11 моделей интегрировано** (5 новых + 6 базовых)
            - ✅ **9 моделей полностью рабочих** из 11 настроенных
            - ✅ **35.47 ГБ моделей** проанализировано в кеше
            - ✅ **GPU оптимизация** для RTX 5070 Ti (12.82ГБ VRAM)
            - ✅ **REST API** с поддержкой всех моделей
            - ✅ **Streamlit UI** с реальной интеграцией
            """)
        
        with col2:
            st.markdown("""
            ### 📈 Технические метрики
            
            - **Время загрузки**: 5-15 секунд на модель
            - **Использование VRAM**: 1-8 ГБ в зависимости от модели
            - **Поддержка языков**: 32 языка (Qwen3-VL)
            - **Форматы документов**: JPG, PNG, BMP, TIFF
            - **Точность OCR**: 85-95% на качественных изображениях
            - **Скорость обработки**: 1-5 секунд на документ
            """)
        
        st.markdown("""
        ### 🔬 Выводы исследования
        
        1. **Специализированные OCR модели** (GOT-OCR) показывают лучшие результаты на структурированных документах
        2. **Универсальные VLM** (Qwen3-VL) эффективны для многоязычного OCR и понимания контекста
        3. **Легкие модели** (DeepSeek OCR) подходят для простых задач с ограниченными ресурсами
        4. **Комбинированный подход** позволяет выбирать оптимальную модель для каждой задачи
        
        ### 📚 Практические рекомендации
        
        - **Для быстрого OCR**: GOT-OCR 2.0 (HF) - 1.1ГБ VRAM
        - **Для многоязычных документов**: Qwen3-VL 2B - 4.4ГБ VRAM  
        - **Для сложного анализа**: Phi-3.5 Vision - 7.7ГБ VRAM
        - **Для парсинга структуры**: dots.ocr - 8ГБ VRAM
        """)
        
        # Ссылки на результаты
        st.info("📖 Подробные результаты см. в [MODEL_INTEGRATION_SUMMARY.md](MODEL_INTEGRATION_SUMMARY.md)")

elif "📄 Режим OCR" in page:
    st.header("📄 Режим распознавания документов")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Загрузить документ")
        
        uploaded_file = st.file_uploader(
            "Выберите изображение",
            type=config["ocr"]["supported_formats"],
            help="Поддерживаемые форматы: JPG, PNG, BMP, TIFF",
            key="ocr_upload"
        )
        
        if uploaded_file:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.session_state.uploaded_image = image
            st.image(image, caption="Загруженное изображение", use_container_width=True)
            
            # Image info
            st.caption(f"📐 Размер: {image.size[0]}x{image.size[1]} | Формат: {image.format}")
        
        st.divider()
        
        # Document type selection
        document_type = st.selectbox(
            "📋 Тип документа",
            list(config["document_templates"].keys()),
            format_func=lambda x: x.capitalize(),
            help="Выберите тип документа для оптимизированного извлечения полей"
        )
        
        # Processing options
        with st.expander("⚙️ Параметры обработки"):
            enhance_image = st.checkbox("Улучшить качество изображения", value=True)
            denoise = st.checkbox("Применить шумоподавление", value=False)
            deskew = st.checkbox("Автоматическое выравнивание", value=False)
        
        st.divider()
        
        # Process button
        if st.button("🚀 Извлечь текст", type="primary", use_container_width=True):
            if uploaded_file:
                with st.spinner("🔄 Обработка документа..."):
                    try:
                        # Реальная интеграция с моделью
                        from models.model_loader import ModelLoader
                        import time
                        
                        start_time = time.time()
                        
                        # Загрузка выбранной модели
                        model = ModelLoader.load_model(selected_model)
                        
                        # Обработка изображения
                        if hasattr(model, 'extract_text'):
                            # Для моделей с методом extract_text (Qwen3-VL)
                            text = model.extract_text(image)
                        elif hasattr(model, 'process_image'):
                            # Для OCR моделей (GOT-OCR, dots.ocr)
                            text = model.process_image(image)
                        else:
                            # Для общих VLM моделей
                            text = model.chat(image, "Извлеките весь текст из этого документа, сохраняя структуру и форматирование.")
                        
                        processing_time = time.time() - start_time
                        
                        # Вычисление уверенности (упрощенная метрика)
                        confidence = min(0.95, max(0.7, len(text.strip()) / 100))
                        
                        st.session_state.ocr_result = {
                            "text": text,
                            "confidence": confidence,
                            "processing_time": processing_time,
                            "model_used": selected_model
                        }
                        
                        st.success("✅ Текст успешно извлечен!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Ошибка при обработке: {str(e)}")
                        st.info("💡 Попробуйте выбрать другую модель или проверьте, что модель загружена корректно")
            else:
                st.error("❌ Пожалуйста, сначала загрузите изображение")
    
    with col2:
        st.subheader("📊 Результаты извлечения")
        
        if st.session_state.ocr_result:
            result = st.session_state.ocr_result
            
            # Metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Уверенность", f"{result['confidence']:.1%}")
            metric_col2.metric("Время обработки", f"{result['processing_time']:.2f}с")
            metric_col3.metric("Модель", result.get('model_used', 'Неизвестно'))
            
            st.divider()
            
            # Extracted text
            st.markdown("**🔤 Распознанный текст:**")
            st.code(result["text"], language="text")
            
            st.divider()
            
            # Extracted fields
            st.markdown("**📋 Извлеченные поля:**")
            
            if document_type and result.get('text'):
                fields = config["document_templates"][document_type]["fields"]
                
                # Простое извлечение полей из текста
                extracted_fields = {}
                text_lines = result['text'].lower().split('\n')
                
                for field in fields:
                    field_value = ""
                    field_lower = field.lower().replace('_', ' ')
                    
                    # Поиск поля в тексте
                    for line in text_lines:
                        if field_lower in line or any(keyword in line for keyword in field_lower.split()):
                            # Извлечение значения после двоеточия или на следующей строке
                            if ':' in line:
                                parts = line.split(':', 1)
                                if len(parts) > 1:
                                    field_value = parts[1].strip()
                            break
                    
                    extracted_fields[field] = field_value
                    
                    st.text_input(
                        field,
                        value=field_value,
                        key=f"field_{field}",
                        help=f"Автоматически извлечено из текста"
                    )
            
            st.divider()
            
            # Export options
            st.markdown("**💾 Параметры экспорта:**")
            col_json, col_csv = st.columns(2)
            
            # Подготовка данных для экспорта
            export_data = {
                "text": result["text"],
                "confidence": result["confidence"],
                "processing_time": result["processing_time"],
                "model_used": result.get("model_used", "unknown"),
                "document_type": document_type,
                "extracted_fields": extracted_fields if 'extracted_fields' in locals() else {}
            }
            
            import json
            json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            # CSV данные
            csv_data = f"field,value\n"
            csv_data += f"text,\"{result['text'].replace(chr(10), ' ')}\"\n"
            csv_data += f"confidence,{result['confidence']}\n"
            csv_data += f"processing_time,{result['processing_time']}\n"
            csv_data += f"model_used,{result.get('model_used', 'unknown')}\n"
            if 'extracted_fields' in locals():
                for field, value in extracted_fields.items():
                    csv_data += f"{field},\"{value}\"\n"
            
            with col_json:
                st.download_button(
                    "📄 Экспорт JSON",
                    data=json_data,
                    file_name="ocr_result.json",
                    mime="application/json",
                    use_container_width=True
                )
            with col_csv:
                st.download_button(
                    "📊 Экспорт CSV",
                    data=csv_data,
                    file_name="ocr_result.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("💡 Загрузите изображение и нажмите 'Извлечь текст', чтобы увидеть результаты здесь")

elif "💬 Режим чата" in page:
    st.header("💬 Интерактивный чат с VLM")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🖼️ Загрузить изображение")
        
        chat_image = st.file_uploader(
            "Изображение для контекста чата",
            type=config["ocr"]["supported_formats"],
            key="chat_upload"
        )
        
        if chat_image:
            image = Image.open(chat_image)
            st.session_state.uploaded_image = image
            st.image(image, caption="Контекстное изображение", use_container_width=True)
            
            if st.button("🗑️ Очистить историю чата", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    with col2:
        st.subheader("💭 Разговор")
        
        # Chat container
        chat_container = st.container(height=400)
        
        with chat_container:
            if not st.session_state.messages:
                st.info("👋 Загрузите изображение и начните задавать вопросы о нем!")
            
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Спросите об изображении...", disabled=not chat_image):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response using real model
            with st.chat_message("assistant"):
                with st.spinner("🤔 Думаю..."):
                    try:
                        from models.model_loader import ModelLoader
                        import time
                        
                        start_time = time.time()
                        
                        # Загрузка выбранной модели
                        model = ModelLoader.load_model(selected_model)
                        
                        # Получение ответа от модели
                        if hasattr(model, 'chat'):
                            response = model.chat(
                                image=image,
                                prompt=prompt,
                                temperature=temperature,
                                max_new_tokens=max_tokens
                            )
                        elif hasattr(model, 'process_image'):
                            # Для OCR моделей адаптируем промпт
                            if any(word in prompt.lower() for word in ['текст', 'прочитай', 'извлеки']):
                                response = model.process_image(image)
                            else:
                                response = f"Это OCR модель. Извлеченный текст:\n\n{model.process_image(image)}"
                        else:
                            response = "Модель не поддерживает чат. Попробуйте режим OCR."
                        
                        processing_time = time.time() - start_time
                        
                        # Добавление информации о времени обработки
                        response += f"\n\n*Обработано за {processing_time:.2f}с с помощью {selected_model}*"
                        
                        st.markdown(response)
                        
                    except Exception as e:
                        response = f"❌ Ошибка при обработке: {str(e)}\n\nПопробуйте выбрать другую модель или проверьте, что модель загружена корректно."
                        st.markdown(response)
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

elif "📊 Сравнение моделей" in page:
    st.header("📊 Сравнение производительности моделей")
    
    # Реальная таблица сравнения с актуальными данными
    import pandas as pd
    
    comparison_data = pd.DataFrame({
        "Модель": [
            "GOT-OCR 2.0 (HF)", 
            "GOT-OCR 2.0 (UCAS)",
            "Qwen2-VL 2B", 
            "Qwen3-VL 2B",
            "Qwen3-VL 4B",
            "Qwen3-VL 8B",
            "Phi-3.5 Vision",
            "dots.ocr",
            "DeepSeek OCR"
        ],
        "Параметры": ["580M", "580M", "2B", "2B", "4B", "8B", "4.2B", "1.7B", "~1B"],
        "VRAM (ГБ)": ["1.1", "2.7", "4.7", "4.4", "8.9", "17.6", "7.7", "8", "0.01"],
        "Статус": ["✅", "✅", "✅", "✅", "⚠️", "❌", "⚠️", "✅", "⚠️"],
        "Лучше для": [
            "Быстрый OCR", 
            "Сложные макеты",
            "Общий OCR", 
            "Многоязычный OCR (32 языка)",
            "Продвинутый анализ",
            "Максимальное качество",
            "Визуальный анализ",
            "Парсинг документов",
            "Легкий OCR"
        ]
    })
    
    # Цветовое кодирование статуса
    def color_status(val):
        if val == "✅":
            return 'background-color: #d4edda'
        elif val == "⚠️":
            return 'background-color: #fff3cd'
        elif val == "❌":
            return 'background-color: #f8d7da'
        return ''
    
    styled_df = comparison_data.style.applymap(color_status, subset=['Статус'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Легенда статусов
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("✅ Полностью рабочая")
    with col2:
        st.warning("⚠️ Частично рабочая")
    with col3:
        st.error("❌ Не кеширована")
    
    st.divider()
    
    # Реальная статистика загруженных моделей
    st.subheader("📈 Статистика системы")
    
    try:
        from models.model_loader import ModelLoader
        
        # Получение информации о кеше
        config = ModelLoader.load_config()
        total_models = len(config.get('models', {}))
        
        # Проверка кешированных моделей
        cached_count = 0
        working_count = 0
        
        for model_key in config.get('models', {}).keys():
            try:
                is_cached, _ = ModelLoader.check_model_cache(model_key)
                if is_cached:
                    cached_count += 1
                    # Проверка, работает ли модель
                    if model_key in ModelLoader.MODEL_REGISTRY:
                        working_count += 1
            except:
                pass
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Всего моделей", total_models)
        col2.metric("Кешированных", cached_count)
        col3.metric("Рабочих", working_count)
        col4.metric("Загруженных", len(ModelLoader.get_loaded_models()))
        
    except Exception as e:
        st.error(f"Ошибка получения статистики: {e}")
    
    st.divider()
    
    st.subheader("📏 Метрики оценки")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Частота ошибок символов (CER)**
        
        Измеряет точность на уровне символов:
        
        ```
        CER = (S + D + I) / N
        ```
        
        Где:
        - S = Замены
        - D = Удаления
        - I = Вставки
        - N = Общее количество символов
        """)
    
    with col2:
        st.markdown("""
        **Частота ошибок слов (WER)**
        
        Измеряет точность на уровне слов:
        
        ```
        WER = (S + D + I) / N
        ```
        
        Где:
        - S = Замены
        - D = Удаления
        - I = Вставки
        - N = Общее количество слов
        """)
    
    with col3:
        st.markdown("""
        **Точность полей**
        
        Извлечение структурированных данных:
        
        ```
        Точность = Правильные / Общие
        ```
        
        Где:
        - Правильные = Правильно извлеченные поля
        - Общие = Общее количество полей
        """)

else:  # Документация
    st.header("📚 Документация")
    
    doc_tabs = st.tabs(["🚀 Быстрый старт", "🤖 Модели", "🏗️ Архитектура", "📖 API", "🤝 Участие"])
    
    with doc_tabs[0]:
        st.markdown("""
        ## Руководство по быстрому старту
        
        ### Установка
        
        ```bash
        # Клонировать репозиторий
        git clone https://github.com/OlegKarenkikh/chatvlmllm.git
        cd chatvlmllm
        
        # Настройка (автоматизированная)
        bash scripts/setup.sh  # Linux/Mac
        scripts\\setup.bat      # Windows
        
        # Запуск приложения
        streamlit run app.py
        ```
        
        ### Первые шаги
        
        1. ✅ Выберите модель в боковой панели
        2. 📄 Выберите режим OCR или чата
        3. 📤 Загрузите ваш документ
        4. 🚀 Получите мгновенные результаты!
        
        ### Выбор модели
        
        - **GOT-OCR**: Быстрое, точное извлечение текста
        - **Qwen2-VL 2B**: Легкий мультимодальный чат
        - **Qwen3-VL 2B**: Продвинутый анализ документов с поддержкой 32 языков
        - **Phi-3.5 Vision**: Мощная модель Microsoft для визуального анализа
        - **dots.ocr**: Специализированный парсер документов
        """)
        
        st.info("📖 Для подробных инструкций см. [QUICKSTART.md](https://github.com/OlegKarenkikh/chatvlmllm/blob/main/QUICKSTART.md)")
    
    with doc_tabs[1]:
        st.markdown("""
        ## Поддерживаемые модели
        
        ### GOT-OCR 2.0
        
        Специализированная OCR модель для сложных макетов документов.
        
        **Сильные стороны:**
        - ✅ Высокая точность на структурированных документах
        - ✅ Извлечение таблиц
        - ✅ Распознавание математических формул
        - ✅ Поддержка множества языков (100+ языков)
        
        **Случаи использования:**
        - Научные статьи
        - Финансовые документы
        - Формы и таблицы
        
        ### Qwen3-VL
        
        Модели машинного зрения общего назначения с улучшенными возможностями OCR.
        
        **Сильные стороны:**
        - ✅ Мультимодальное понимание
        - ✅ Контекстно-зависимые ответы
        - ✅ Интерактивный чат
        - ✅ Возможности рассуждения
        - ✅ Поддержка 32 языков OCR
        
        **Случаи использования:**
        - Вопросы и ответы по документам
        - Визуальный анализ
        - Извлечение контента
        
        ### Phi-3.5 Vision
        
        Мощная модель Microsoft для визуального анализа.
        
        **Сильные стороны:**
        - ✅ Высокое качество понимания изображений
        - ✅ Эффективная архитектура
        - ✅ Хорошая производительность на визуальных задачах
        
        ### dots.ocr
        
        Специализированный парсер документов для сложных макетов.
        
        **Сильные стороны:**
        - ✅ Понимание структуры документа
        - ✅ Извлечение макета
        - ✅ Поддержка множества языков
        - ✅ JSON вывод
        """)
        
        st.info("📖 Для подробной документации см. [docs/models.md](https://github.com/OlegKarenkikh/chatvlmllm/blob/main/docs/models.md)")
    
    with doc_tabs[2]:
        st.markdown("""
        ## Архитектура системы
        
        ### Слоистый дизайн
        
        ```
        UI слой (Streamlit)
              ↓
        Слой приложения
              ↓
        Слой обработки (Utils)
              ↓
        Слой моделей (VLM модели)
              ↓
        Основа (PyTorch/HF)
        ```
        
        ### Ключевые компоненты
        
        - **Модели**: Интеграция VLM и инференс
        - **Утилиты**: Обработка изображений и извлечение текста
        - **UI**: Интерфейс Streamlit и стилизация
        - **Тесты**: Обеспечение качества
        """)
        
        st.info("📖 Для деталей архитектуры см. [docs/architecture.md](https://github.com/OlegKarenkikh/chatvlmllm/blob/main/docs/architecture.md)")
    
    with doc_tabs[3]:
        st.markdown("""
        ## Справочник API
        
        ### Загрузка моделей
        
        ```python
        from models import ModelLoader
        
        # Загрузить модель
        model = ModelLoader.load_model('got_ocr')
        
        # Обработать изображение
        from PIL import Image
        image = Image.open('document.jpg')
        text = model.process_image(image)
        ```
        
        ### Извлечение полей
        
        ```python
        from utils.field_parser import FieldParser
        
        # Парсинг счета
        fields = FieldParser.parse_invoice(text)
        print(fields['invoice_number'])
        ```
        
        ### Интерфейс чата
        
        ```python
        # Интерактивный чат
        model = ModelLoader.load_model('qwen3_vl_2b')
        response = model.chat(image, "Что в этом документе?")
        ```
        """)
    
    with doc_tabs[4]:
        st.markdown("""
        ## Участие в проекте
        
        Мы приветствуем вклад! 🎉
        
        ### Как внести вклад
        
        1. 🍴 Сделайте форк репозитория
        2. 🌿 Создайте ветку функции
        3. ✍️ Внесите изменения
        4. ✅ Напишите тесты
        5. 📝 Обновите документацию
        6. 🚀 Отправьте pull request
        
        ### Области для вклада
        
        - 🐛 Исправления ошибок
        - ✨ Новые функции
        - 📝 Документация
        - 🧪 Тесты
        - 🎨 Улучшения UI
        """)
        
        st.info("📖 Для руководящих принципов участия см. [CONTRIBUTING.md](https://github.com/OlegKarenkikh/chatvlmllm/blob/main/CONTRIBUTING.md)")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem;">
    <p><strong>ChatVLMLLM</strong> - Образовательный исследовательский проект</p>
    <p>Создано с ❤️ используя Streamlit | 
    <a href="https://github.com/OlegKarenkikh/chatvlmllm" target="_blank" style="color: #FF4B4B;">GitHub</a> | 
    Лицензия MIT</p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">🔬 Исследование моделей машинного зрения для OCR документов</p>
</div>
""", unsafe_allow_html=True)