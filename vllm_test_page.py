#!/usr/bin/env python3
"""
Тестовая страница для vLLM интеграции
"""

import streamlit as st
from vllm_streamlit_adapter import create_vllm_interface

def main():
    st.set_page_config(
        page_title="vLLM Test Interface",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 Тестирование vLLM Интеграции")
    st.markdown("---")
    
    # Информация о системе
    with st.expander("ℹ️ Информация о системе"):
        st.markdown("""
        **Текущая конфигурация:**
        - 🐳 vLLM сервер: Docker Compose (порт 8000)
        - 🤖 Модель: rednote-hilab/dots.ocr
        - 💾 GPU память: 5.72 ГБ
        - ⚡ Flash Attention: Активен
        - 🔧 Режим: Eager execution
        """)
    
    # Основной интерфейс
    create_vllm_interface()
    
    # Дополнительная информация
    st.markdown("---")
    st.markdown("""
    ### 🔧 Управление vLLM сервером
    
    **Команды Docker Compose:**
    ```bash
    # Просмотр логов
    docker-compose -f docker-compose-vllm.yml logs dots-ocr
    
    # Перезапуск
    docker-compose -f docker-compose-vllm.yml restart dots-ocr
    
    # Остановка
    docker-compose -f docker-compose-vllm.yml stop dots-ocr
    ```
    
    **Прямое тестирование API:**
    ```bash
    # Health check
    curl http://localhost:8000/health
    
    # Список моделей
    curl http://localhost:8000/v1/models
    ```
    """)

if __name__ == "__main__":
    main()