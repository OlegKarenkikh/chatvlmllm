#!/usr/bin/env python3
"""
Переключатель режимов с контролем памяти для Streamlit
Интеграция MemoryController в пользовательский интерфейс
"""

import streamlit as st
import time
from typing import Tuple, Dict, Any, List
from utils.memory_controller import memory_controller, ExecutionMode
import subprocess
import json

class ModeSwitcher:
    """Переключатель режимов выполнения с контролем памяти"""
    
    def __init__(self):
        self.memory_controller = memory_controller
        
        # Инициализация состояния сессии
        if 'current_execution_mode' not in st.session_state:
            st.session_state.current_execution_mode = None
        if 'current_model' not in st.session_state:
            st.session_state.current_model = None
        if 'memory_status' not in st.session_state:
            st.session_state.memory_status = {}
    
    def display_memory_status(self) -> None:
        """Отображение статуса памяти"""
        status = self.memory_controller.get_memory_status()
        st.session_state.memory_status = status
        
        # GPU память
        gpu_mem = status['gpu_memory']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "GPU память (всего)", 
                f"{gpu_mem['total_gb']:.1f} GB",
                help="Общий объем GPU памяти"
            )
        
        with col2:
            st.metric(
                "Используется", 
                f"{gpu_mem['used_gb']:.1f} GB",
                f"{gpu_mem['utilization_percent']:.1f}%",
                help="Используемая GPU память"
            )
        
        with col3:
            st.metric(
                "Доступно", 
                f"{gpu_mem['free_gb']:.1f} GB",
                help="Доступная GPU память"
            )
        
        # Индикатор состояния памяти
        if gpu_mem['free_gb'] < 2.0:
            st.error("⚠️ Критически мало свободной GPU памяти")
        elif gpu_mem['free_gb'] < 4.0:
            st.warning("⚠️ Мало свободной GPU памяти")
        else:
            st.success("✅ Достаточно свободной GPU памяти")
        
        # Текущий режим
        current_mode = status.get('current_mode')
        if current_mode:
            st.info(f"🔧 Текущий режим: **{current_mode.upper()}**")
        else:
            st.info("🔧 Режим не определен")
    
    def display_loaded_models(self) -> None:
        """Отображение загруженных моделей"""
        status = self.memory_controller.get_memory_status()
        loaded_models = status['loaded_models']
        
        st.subheader("📦 Загруженные модели")
        
        # Transformers модели
        transformers_models = loaded_models['transformers']
        if transformers_models:
            st.write("**Transformers модели:**")
            for model in transformers_models:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {model}")
                with col2:
                    if st.button("🗑️", key=f"unload_tf_{model}", help=f"Выгрузить {model}"):
                        self.unload_transformers_model(model)
        else:
            st.write("*Нет загруженных Transformers моделей*")
        
        # vLLM контейнеры
        vllm_containers = loaded_models['vllm_containers']
        if vllm_containers:
            st.write("**vLLM контейнеры:**")
            for container in vllm_containers:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {container}")
                with col2:
                    if st.button("🛑", key=f"stop_vllm_{container}", help=f"Остановить {container}"):
                        self.stop_vllm_container(container)
        else:
            st.write("*Нет запущенных vLLM контейнеров*")
    
    def display_cached_models(self) -> None:
        """Отображение кешированных моделей"""
        cached_models = self.memory_controller.get_cached_models()
        
        st.subheader("💾 Кешированные модели")
        
        if cached_models:
            for model in cached_models:
                st.write(f"• {model}")
        else:
            st.warning("Нет кешированных моделей")
            st.info("Запустите загрузку моделей для создания кеша")
    
    def switch_execution_mode(self, target_mode: str, target_model: str = None) -> Tuple[bool, str]:
        """Переключение режима выполнения"""
        
        if target_mode == "vLLM (Рекомендуется)":
            mode = ExecutionMode.VLLM
        else:
            mode = ExecutionMode.TRANSFORMERS
        
        # Показываем прогресс
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔄 Подготовка к переключению режима...")
            progress_bar.progress(20)
            
            if mode == ExecutionMode.VLLM:
                success, message = self.memory_controller.switch_to_vllm_mode(target_model)
            else:
                success, message = self.memory_controller.switch_to_transformers_mode(target_model)
            
            progress_bar.progress(80)
            
            if success:
                st.session_state.current_execution_mode = target_mode
                if target_model:
                    st.session_state.current_model = target_model
                
                status_text.text("✅ Переключение завершено")
                progress_bar.progress(100)
                time.sleep(1)
                
                # Очищаем прогресс
                progress_bar.empty()
                status_text.empty()
                
                return True, message
            else:
                progress_bar.empty()
                status_text.empty()
                return False, message
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            return False, f"Ошибка переключения режима: {e}"
    
    def change_model(self, new_model: str, execution_mode: str) -> Tuple[bool, str]:
        """Смена модели с контролем памяти"""
        
        container_type = "vllm" if "vLLM" in execution_mode else "transformers"
        
        # Показываем прогресс
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text(f"🔄 Смена модели на {new_model}...")
            progress_bar.progress(30)
            
            success, message = self.memory_controller.change_model_in_container(
                new_model, container_type
            )
            
            progress_bar.progress(80)
            
            if success:
                st.session_state.current_model = new_model
                status_text.text("✅ Модель успешно изменена")
                progress_bar.progress(100)
                time.sleep(1)
                
                # Очищаем прогресс
                progress_bar.empty()
                status_text.empty()
                
                return True, message
            else:
                progress_bar.empty()
                status_text.empty()
                return False, message
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            return False, f"Ошибка смены модели: {e}"
    
    def unload_transformers_model(self, model_name: str) -> None:
        """Выгрузка Transformers модели"""
        with st.spinner(f"Выгрузка модели {model_name}..."):
            unloaded = self.memory_controller.unload_transformers_models([model_name])
            
            if unloaded:
                st.success(f"✅ Модель {model_name} выгружена")
                st.rerun()
            else:
                st.error(f"❌ Не удалось выгрузить модель {model_name}")
    
    def stop_vllm_container(self, container_name: str) -> None:
        """Остановка vLLM контейнера"""
        with st.spinner(f"Остановка контейнера {container_name}..."):
            # Извлекаем имя модели из имени контейнера
            model_names = [container_name]  # Упрощенная логика
            stopped = self.memory_controller.stop_vllm_containers(model_names)
            
            if stopped:
                st.success(f"✅ Контейнер {container_name} остановлен")
                st.rerun()
            else:
                st.error(f"❌ Не удалось остановить контейнер {container_name}")
    
    def emergency_cleanup(self) -> None:
        """Экстренная очистка памяти"""
        with st.spinner("🚨 Экстренная очистка памяти..."):
            success, message = self.memory_controller.emergency_cleanup()
            
            if success:
                st.success("✅ Экстренная очистка завершена")
                st.info(message)
                
                # Сбрасываем состояние сессии
                st.session_state.current_execution_mode = None
                st.session_state.current_model = None
                
                st.rerun()
            else:
                st.error(f"❌ Ошибка экстренной очистки: {message}")
    
    def display_mode_switcher_ui(self) -> None:
        """Отображение UI переключателя режимов"""
        
        st.subheader("🔧 Управление режимами выполнения")
        
        # Текущий статус
        with st.expander("📊 Статус памяти", expanded=True):
            self.display_memory_status()
        
        # Переключение режима
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Режим выполнения:**")
            execution_mode = st.selectbox(
                "Выберите режим",
                ["vLLM (Рекомендуется)", "Transformers (Локально)"],
                index=0 if st.session_state.current_execution_mode == "vLLM (Рекомендуется)" else 1,
                key="execution_mode_selector"
            )
        
        with col2:
            st.write("**Модель:**")
            cached_models = self.memory_controller.get_cached_models()
            
            if cached_models:
                current_model_index = 0
                if st.session_state.current_model in cached_models:
                    current_model_index = cached_models.index(st.session_state.current_model)
                
                selected_model = st.selectbox(
                    "Выберите модель",
                    cached_models,
                    index=current_model_index,
                    key="model_selector"
                )
            else:
                st.warning("Нет кешированных моделей")
                selected_model = None
        
        # Кнопки управления
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Применить изменения", type="primary"):
                if selected_model:
                    # Проверяем, нужно ли переключать режим
                    if execution_mode != st.session_state.current_execution_mode:
                        success, message = self.switch_execution_mode(execution_mode, selected_model)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
                    
                    # Проверяем, нужно ли менять модель
                    elif selected_model != st.session_state.current_model:
                        success, message = self.change_model(selected_model, execution_mode)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.info("Изменений нет")
                else:
                    st.error("Выберите модель")
        
        with col2:
            if st.button("🧹 Очистить память"):
                self.memory_controller.cleanup_gpu_memory()
                st.success("✅ GPU память очищена")
                st.rerun()
        
        with col3:
            if st.button("🚨 Экстренная очистка"):
                self.emergency_cleanup()
        
        # Детальная информация
        with st.expander("📦 Управление моделями"):
            self.display_loaded_models()
        
        with st.expander("💾 Кешированные модели"):
            self.display_cached_models()
    
    def get_recommended_settings(self) -> Dict[str, Any]:
        """Получение рекомендуемых настроек на основе памяти"""
        status = self.memory_controller.get_memory_status()
        gpu_mem = status['gpu_memory']
        
        recommendations = {
            "execution_mode": "transformers",  # По умолчанию
            "precision": "fp16",
            "quantization": False,
            "max_tokens": 1024,
            "batch_size": 1
        }
        
        # Рекомендации на основе доступной памяти
        free_gb = gpu_mem['free_gb']
        
        if free_gb >= 8.0:
            recommendations.update({
                "execution_mode": "vllm",
                "precision": "fp16",
                "max_tokens": 2048,
                "batch_size": 4
            })
        elif free_gb >= 6.0:
            recommendations.update({
                "execution_mode": "vllm",
                "precision": "fp16",
                "max_tokens": 1024,
                "batch_size": 2
            })
        elif free_gb >= 4.0:
            recommendations.update({
                "execution_mode": "transformers",
                "precision": "fp16",
                "max_tokens": 1024,
                "batch_size": 1
            })
        else:
            recommendations.update({
                "execution_mode": "transformers",
                "precision": "int8",
                "quantization": True,
                "max_tokens": 512,
                "batch_size": 1
            })
        
        return recommendations

# Глобальный экземпляр переключателя
mode_switcher = ModeSwitcher()