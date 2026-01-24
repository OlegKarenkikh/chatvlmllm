#!/usr/bin/env python3
"""
Адаптер для интеграции vLLM API с Streamlit интерфейсом
"""

import requests
import base64
import time
import streamlit as st
from PIL import Image
import io
from typing import Optional, Dict, Any

class VLLMStreamlitAdapter:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.available_models = []
        self.check_connection()
    
    def check_connection(self) -> bool:
        """Проверка подключения к vLLM серверу"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.get_available_models()
                return True
        except Exception as e:
            st.error(f"❌ Не удается подключиться к vLLM серверу: {e}")
        return False
    
    def get_available_models(self) -> list:
        """Получение списка доступных моделей"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = []
                self.model_limits = {}
                
                for model in models_data.get("data", []):
                    model_id = model["id"]
                    max_tokens = model.get("max_model_len", 1024)
                    
                    self.available_models.append(model_id)
                    self.model_limits[model_id] = max_tokens
                
                return self.available_models
        except Exception as e:
            st.error(f"❌ Ошибка получения моделей: {e}")
        return []
    
    def get_model_max_tokens(self, model_id: str) -> int:
        """Получение максимального количества токенов для модели"""
        return getattr(self, 'model_limits', {}).get(model_id, 1024)
    
    def chat_with_image(self, image: Image.Image, prompt: str, 
                       model: str = "rednote-hilab/dots.ocr") -> Optional[Dict[str, Any]]:
        """Чат с изображением через vLLM API"""
        return self.process_image(image, prompt, model)
    
    def process_image(self, image: Image.Image, prompt: str = "Extract all text from this image", 
                     model: str = "rednote-hilab/dots.ocr", max_tokens: int = 4096) -> Optional[Dict[str, Any]]:
        """Обработка изображения через vLLM API"""
        
        # Проверяем лимит токенов для модели
        model_max_tokens = self.get_model_max_tokens(model)
        
        # УЛУЧШЕНИЕ: Более детальная проверка токенов
        if max_tokens > model_max_tokens:
            st.warning(f"⚠️ Запрошено {max_tokens} токенов, но модель {model} поддерживает максимум {model_max_tokens}")
            max_tokens = model_max_tokens
        
        # Дополнительная проверка: оставляем место для входных токенов
        estimated_input_tokens = len(prompt.split()) * 1.3 + 200  # Примерная оценка: промпт + изображение
        if max_tokens + estimated_input_tokens > model_max_tokens:
            adjusted_tokens = max(100, model_max_tokens - int(estimated_input_tokens))
            st.info(f"🔧 Автоматически скорректированы токены: {max_tokens} → {adjusted_tokens} (резерв для входных токенов)")
            max_tokens = adjusted_tokens
        
        # Конвертация изображения в base64
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Подготовка запроса
        payload = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": max_tokens,  # Ограниченное количество токенов
            "temperature": 0.1
        }
        
        try:
            # Отправка запроса
            start_time = time.time()
            
            with st.spinner(f"🔄 Обработка изображения через vLLM (макс. {max_tokens} токенов)..."):
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=120
                )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                return {
                    "success": True,
                    "text": content,
                    "processing_time": processing_time,
                    "model": model,
                    "mode": "vLLM",
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                    "max_tokens_limit": model_max_tokens,
                    "actual_max_tokens": max_tokens
                }
            else:
                error_text = response.text
                st.error(f"❌ API ошибка: {response.status_code}")
                
                # Специальная обработка ошибок валидации токенов
                if "max_tokens" in error_text and "exceeds" in error_text:
                    st.error("🚨 **ОШИБКА ЛИМИТА ТОКЕНОВ**")
                    st.error(f"Запрошено токенов: {max_tokens}")
                    st.error(f"Лимит модели: {model_max_tokens}")
                    st.info("💡 **Решение:** Уменьшите количество токенов в настройках или используйте автоматическую коррекцию")
                
                st.error(f"Ответ сервера: {error_text}")
                return None
                
        except Exception as e:
            st.error(f"❌ Ошибка обработки: {e}")
            return None
    
    def get_server_status(self) -> Dict[str, Any]:
        """Получение статуса сервера"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "url": self.base_url,
                    "models": len(self.available_models),
                    "available_models": self.available_models,
                    "model_limits": getattr(self, 'model_limits', {})
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": self.base_url
            }
        
        return {"status": "unknown"}

def create_vllm_interface():
    """Создание интерфейса для работы с vLLM"""
    st.header("🚀 vLLM Режим")
    
    # Инициализация адаптера
    if "vllm_adapter" not in st.session_state:
        st.session_state.vllm_adapter = VLLMStreamlitAdapter()
    
    adapter = st.session_state.vllm_adapter
    
    # Статус сервера
    status = adapter.get_server_status()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if status["status"] == "healthy":
            st.success("✅ vLLM Сервер")
        else:
            st.error("❌ vLLM Недоступен")
    
    with col2:
        st.info(f"🌐 {status['url']}")
    
    with col3:
        if status["status"] == "healthy":
            st.info(f"🤖 Моделей: {status['models']}")
    
    if status["status"] != "healthy":
        st.error("❌ vLLM сервер недоступен. Убедитесь, что контейнер запущен:")
        st.code("docker-compose -f docker-compose-vllm.yml up -d dots-ocr")
        return
    
    # Выбор модели
    if adapter.available_models:
        selected_model = st.selectbox(
            "🤖 Выберите модель",
            adapter.available_models,
            help="Доступные модели в vLLM сервере"
        )
    else:
        st.error("❌ Нет доступных моделей")
        return
    
    # Настройки промпта
    st.subheader("📝 Настройки обработки")
    
    prompt_type = st.selectbox(
        "Тип задачи",
        [
            "Extract all text from this image",
            "Describe what you see in this image",
            "Extract structured data from this document",
            "Identify and extract key information",
            "Custom prompt"
        ]
    )
    
    if prompt_type == "Custom prompt":
        custom_prompt = st.text_area(
            "Введите свой промпт",
            value="Extract all text from this image",
            help="Опишите, что должна сделать модель с изображением"
        )
        prompt = custom_prompt
    else:
        prompt = prompt_type
    
    # Загрузка изображения
    st.subheader("📷 Загрузка изображения")
    
    uploaded_file = st.file_uploader(
        "Выберите изображение",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        help="Поддерживаемые форматы: PNG, JPG, JPEG, BMP, TIFF"
    )
    
    if uploaded_file is not None:
        # Отображение изображения
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(image, caption="Загруженное изображение", use_column_width=True)
            st.info(f"📏 Размер: {image.size[0]}x{image.size[1]}")
        
        with col2:
            if st.button("🚀 Обработать изображение", type="primary", use_container_width=True):
                result = adapter.process_image(image, prompt, selected_model)
                
                if result and result["success"]:
                    st.success("✅ Обработка завершена!")
                    
                    # Результат
                    st.subheader("📄 Результат OCR")
                    st.text_area(
                        "Извлеченный текст",
                        value=result["text"],
                        height=200,
                        help="Результат обработки изображения"
                    )
                    
                    # Метрики
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("⏱️ Время", f"{result['processing_time']:.1f} сек")
                    
                    with col2:
                        st.metric("🤖 Модель", result["model"].split("/")[-1])
                    
                    with col3:
                        st.metric("🔧 Режим", result["mode"])
                    
                    # Дополнительная информация
                    with st.expander("📊 Подробная информация"):
                        st.json({
                            "model": result["model"],
                            "processing_time": result["processing_time"],
                            "tokens_used": result.get("tokens_used", 0),
                            "mode": result["mode"],
                            "prompt": prompt
                        })
                    
                    # Кнопки экспорта
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📋 Копировать текст"):
                            st.write("Текст скопирован в буфер обмена!")
                    
                    with col2:
                        # Экспорт в JSON
                        export_data = {
                            "text": result["text"],
                            "model": result["model"],
                            "processing_time": result["processing_time"],
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        st.download_button(
                            "💾 Скачать JSON",
                            data=str(export_data),
                            file_name=f"ocr_result_{int(time.time())}.json",
                            mime="application/json"
                        )

if __name__ == "__main__":
    create_vllm_interface()