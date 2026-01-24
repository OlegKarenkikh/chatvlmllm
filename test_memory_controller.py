#!/usr/bin/env python3
"""
Тест контроллера памяти для переключения режимов
"""

import streamlit as st
import time
from utils.memory_controller import memory_controller, ExecutionMode
from utils.mode_switcher import mode_switcher

def test_memory_controller():
    """Тестирование контроллера памяти"""
    
    st.title("🧪 Тест контроллера памяти")
    st.caption("Проверка функций управления памятью и переключения режимов")
    
    # Основная информация
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Статус памяти")
        
        if st.button("🔄 Обновить статус"):
            st.rerun()
        
        # Получение статуса памяти
        status = memory_controller.get_memory_status()
        
        # GPU память
        gpu_mem = status['gpu_memory']
        st.metric("GPU память (всего)", f"{gpu_mem['total_gb']:.1f} GB")
        st.metric("Используется", f"{gpu_mem['used_gb']:.1f} GB")
        st.metric("Доступно", f"{gpu_mem['free_gb']:.1f} GB")
        st.metric("Утилизация", f"{gpu_mem['utilization_percent']:.1f}%")
        
        # Текущий режим
        current_mode = status.get('current_mode')
        if current_mode:
            st.success(f"Текущий режим: {current_mode}")
        else:
            st.info("Режим не определен")
    
    with col2:
        st.subheader("🔧 Управление")
        
        # Тест переключения режимов
        st.write("**Переключение режимов:**")
        
        col_vllm, col_tf = st.columns(2)
        
        with col_vllm:
            if st.button("🚀 Переключить на vLLM"):
                with st.spinner("Переключение на vLLM..."):
                    success, message = memory_controller.switch_to_vllm_mode()
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                    st.rerun()
        
        with col_tf:
            if st.button("🔧 Переключить на Transformers"):
                with st.spinner("Переключение на Transformers..."):
                    success, message = memory_controller.switch_to_transformers_mode()
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                    st.rerun()
        
        # Очистка памяти
        st.write("**Очистка памяти:**")
        
        col_clean, col_emergency = st.columns(2)
        
        with col_clean:
            if st.button("🧹 Очистить GPU"):
                with st.spinner("Очистка GPU памяти..."):
                    success = memory_controller.cleanup_gpu_memory()
                    if success:
                        st.success("✅ GPU память очищена")
                    else:
                        st.error("❌ Ошибка очистки")
                    st.rerun()
        
        with col_emergency:
            if st.button("🚨 Экстренная очистка"):
                with st.spinner("Экстренная очистка..."):
                    success, message = memory_controller.emergency_cleanup()
                    if success:
                        st.success("✅ Экстренная очистка завершена")
                        st.info(message)
                    else:
                        st.error(f"❌ {message}")
                    st.rerun()
    
    # Детальная информация
    st.divider()
    
    # Загруженные модели
    st.subheader("📦 Загруженные модели")
    
    loaded_models = status['loaded_models']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Transformers модели:**")
        transformers_models = loaded_models['transformers']
        if transformers_models:
            for model in transformers_models:
                st.write(f"• {model}")
        else:
            st.write("*Нет загруженных моделей*")
    
    with col2:
        st.write("**vLLM контейнеры:**")
        vllm_containers = loaded_models['vllm_containers']
        if vllm_containers:
            for container in vllm_containers:
                st.write(f"• {container}")
        else:
            st.write("*Нет запущенных контейнеров*")
    
    # Кешированные модели
    st.subheader("💾 Кешированные модели")
    
    cached_models = status['cached_models']
    if cached_models:
        for model in cached_models:
            st.write(f"• {model}")
    else:
        st.warning("Нет кешированных моделей")
    
    # Тест смены модели
    st.divider()
    st.subheader("🔄 Тест смены модели")
    
    if cached_models:
        selected_model = st.selectbox("Выберите модель для загрузки:", cached_models)
        execution_type = st.selectbox("Тип выполнения:", ["transformers", "vllm"])
        
        if st.button("🔄 Сменить модель"):
            with st.spinner(f"Смена модели на {selected_model}..."):
                success, message = memory_controller.change_model_in_container(
                    selected_model, execution_type
                )
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
                st.rerun()
    else:
        st.info("Нет кешированных моделей для тестирования")
    
    # Полный статус (JSON)
    with st.expander("🔍 Полный статус (JSON)"):
        st.json(status)
    
    # Рекомендации
    st.divider()
    st.subheader("💡 Рекомендации")
    
    recommendations = mode_switcher.get_recommended_settings()
    
    st.write("**Рекомендуемые настройки на основе доступной памяти:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"• Режим выполнения: **{recommendations['execution_mode']}**")
        st.write(f"• Точность: **{recommendations['precision']}**")
        st.write(f"• Квантизация: **{recommendations['quantization']}**")
    
    with col2:
        st.write(f"• Максимум токенов: **{recommendations['max_tokens']}**")
        st.write(f"• Размер батча: **{recommendations['batch_size']}**")
    
    # Автообновление
    if st.checkbox("🔄 Автообновление (каждые 5 сек)"):
        time.sleep(5)
        st.rerun()

def main():
    """Главная функция"""
    
    st.set_page_config(
        page_title="Тест контроллера памяти",
        page_icon="🧪",
        layout="wide"
    )
    
    test_memory_controller()

if __name__ == "__main__":
    main()