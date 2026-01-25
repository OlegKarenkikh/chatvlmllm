#!/usr/bin/env python3
"""
Менеджер одиночных контейнеров для vLLM
Строгий принцип: только ОДИН активный контейнер одновременно
"""

import docker
import requests
import time
import json
import subprocess
from typing import Dict, List, Optional, Tuple
import streamlit as st

class SingleContainerManager:
    def __init__(self):
        self.client = docker.from_env()
        
        # Конфигурация доступных моделей
        self.models_config = {
            "dots.ocr": {
                "container_name": "dots-ocr-fixed",
                "compose_service": "dots-ocr",
                "port": 8000,
                "model_path": "rednote-hilab/dots.ocr",
                "display_name": "dots.ocr (OCR специалист)",
                "memory_gb": 4.5,
                "startup_time": 60,  # секунды
                "description": "Специализированная OCR модель для документов"
            },
            "qwen3-vl-2b": {
                "container_name": "qwen-qwen3-vl-2b-instruct-vllm",
                "compose_service": "qwen3-vl-2b",
                "port": 8004,
                "model_path": "Qwen/Qwen3-VL-2B-Instruct",
                "display_name": "Qwen3-VL 2B (Рекомендуется)",
                "memory_gb": 6.5,
                "startup_time": 120,
                "description": "Универсальная VLM модель с высокой точностью"
            },
            "qwen2-vl-2b": {
                "container_name": "qwen-qwen2-vl-2b-instruct-vllm",
                "compose_service": "qwen2-vl-2b",
                "port": 8001,
                "model_path": "Qwen/Qwen2-VL-2B-Instruct",
                "display_name": "Qwen2-VL 2B (Стабильная)",
                "memory_gb": 6.0,
                "startup_time": 100,
                "description": "Стабильная VLM модель для общих задач"
            },
            "phi35-vision": {
                "container_name": "microsoft-phi-3-5-vision-instruct-vllm",
                "compose_service": "phi35-vision",
                "port": 8002,
                "model_path": "microsoft/Phi-3.5-vision-instruct",
                "display_name": "Phi-3.5 Vision (Продвинутая)",
                "memory_gb": 8.0,
                "startup_time": 150,
                "description": "Продвинутая модель Microsoft для сложных задач"
            }
        }
        
        self.compose_file = "docker-compose-vllm.yml"
        self.current_active_model = None
    
    def get_container_status(self, container_name: str) -> Dict:
        """Получение детального статуса контейнера"""
        try:
            container = self.client.containers.get(container_name)
            
            # Получаем health status
            health_status = "unknown"
            if "Health" in container.attrs.get("State", {}):
                health_status = container.attrs["State"]["Health"]["Status"]
            
            return {
                "exists": True,
                "running": container.status == "running",
                "status": container.status,
                "health": health_status,
                "created": container.attrs.get("Created", ""),
                "started_at": container.attrs.get("State", {}).get("StartedAt", "")
            }
        except docker.errors.NotFound:
            return {
                "exists": False,
                "running": False,
                "status": "not_found",
                "health": "unknown"
            }
        except Exception as e:
            return {
                "exists": False,
                "running": False,
                "status": "error",
                "health": "unknown",
                "error": str(e)
            }
    
    def check_api_health(self, port: int, timeout: int = 5) -> Tuple[bool, str]:
        """Проверка здоровья API модели"""
        try:
            # Health check
            response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
            if response.status_code != 200:
                return False, f"Health check failed: {response.status_code}"
            
            # Models check
            models_response = requests.get(f"http://localhost:{port}/v1/models", timeout=timeout)
            if models_response.status_code != 200:
                return False, f"Models endpoint failed: {models_response.status_code}"
            
            models_data = models_response.json()
            if not models_data.get("data"):
                return False, "No models available"
            
            return True, "API healthy"
            
        except requests.exceptions.ConnectionError:
            return False, "Connection refused"
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except Exception as e:
            return False, f"API error: {str(e)}"
    
    def get_active_model(self) -> Optional[str]:
        """Определение текущей активной модели"""
        for model_key, config in self.models_config.items():
            container_status = self.get_container_status(config["container_name"])
            
            if container_status["running"] and container_status["health"] == "healthy":
                api_healthy, _ = self.check_api_health(config["port"])
                if api_healthy:
                    self.current_active_model = model_key
                    return model_key
        
        self.current_active_model = None
        return None
    
    def stop_all_containers(self) -> Tuple[List[str], List[str]]:
        """Остановка всех vLLM контейнеров"""
        stopped = []
        failed = []
        
        for model_key, config in self.models_config.items():
            container_status = self.get_container_status(config["container_name"])
            
            if container_status["running"]:
                try:
                    result = subprocess.run([
                        "docker-compose", "-f", self.compose_file,
                        "stop", config["compose_service"]
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        stopped.append(model_key)
                    else:
                        failed.append(f"{model_key}: {result.stderr}")
                        
                except Exception as e:
                    failed.append(f"{model_key}: {str(e)}")
        
        return stopped, failed
    
    def start_single_container(self, model_key: str) -> Tuple[bool, str]:
        """Запуск одного контейнера (с остановкой всех остальных)"""
        
        if model_key not in self.models_config:
            return False, f"Модель {model_key} не найдена в конфигурации"
        
        config = self.models_config[model_key]
        
        # Шаг 1: Останавливаем все контейнеры
        st.info("🛑 Остановка всех активных контейнеров...")
        stopped, failed = self.stop_all_containers()
        
        if stopped:
            stopped_names = [self.models_config[m]["display_name"] for m in stopped]
            st.success(f"✅ Остановлены: {', '.join(stopped_names)}")
        
        if failed:
            st.warning(f"⚠️ Ошибки остановки: {'; '.join(failed)}")
        
        # Пауза для освобождения памяти
        time.sleep(3)
        
        # Шаг 2: Запускаем целевой контейнер
        st.info(f"🚀 Запуск {config['display_name']}...")
        
        try:
            result = subprocess.run([
                "docker-compose", "-f", self.compose_file,
                "up", "-d", config["compose_service"]
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return False, f"Ошибка запуска контейнера: {result.stderr}"
            
            # Шаг 3: Ожидание готовности
            st.info(f"⏳ Ожидание готовности модели (до {config['startup_time']} сек)...")
            
            start_time = time.time()
            max_wait = config["startup_time"]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            while time.time() - start_time < max_wait:
                elapsed = time.time() - start_time
                progress = min(elapsed / max_wait, 1.0)
                progress_bar.progress(progress)
                
                # Проверяем статус контейнера
                container_status = self.get_container_status(config["container_name"])
                
                if container_status["running"]:
                    # Проверяем API
                    api_healthy, api_message = self.check_api_health(config["port"], timeout=3)
                    
                    if api_healthy:
                        progress_bar.progress(1.0)
                        status_text.success(f"✅ {config['display_name']} готов к работе!")
                        self.current_active_model = model_key
                        return True, f"Модель {config['display_name']} успешно запущена"
                    else:
                        status_text.info(f"🔄 Загрузка модели... ({api_message})")
                else:
                    status_text.info(f"🔄 Запуск контейнера... ({container_status['status']})")
                
                time.sleep(2)
            
            # Таймаут
            progress_bar.empty()
            status_text.empty()
            return False, f"Таймаут запуска модели {config['display_name']} ({max_wait} сек)"
            
        except Exception as e:
            return False, f"Ошибка запуска: {str(e)}"
    
    def get_system_status(self) -> Dict:
        """Получение полного статуса системы"""
        active_model = self.get_active_model()
        
        models_status = {}
        total_memory = 0
        
        for model_key, config in self.models_config.items():
            container_status = self.get_container_status(config["container_name"])
            api_healthy = False
            api_message = "Not checked"
            
            if container_status["running"]:
                api_healthy, api_message = self.check_api_health(config["port"])
                if api_healthy:
                    total_memory += config["memory_gb"]
            
            models_status[model_key] = {
                "config": config,
                "container_status": container_status,
                "api_healthy": api_healthy,
                "api_message": api_message,
                "is_active": model_key == active_model
            }
        
        return {
            "active_model": active_model,
            "active_model_name": self.models_config[active_model]["display_name"] if active_model else None,
            "total_memory_usage": total_memory,
            "models": models_status,
            "principle": "single_container_only"
        }
    
    def create_model_selector_ui(self) -> Optional[str]:
        """UI для выбора модели с автоматическим переключением"""
        
        st.subheader("🎯 Выбор активной модели")
        st.info("💡 **Принцип работы:** Только одна модель активна одновременно для экономии GPU памяти")
        
        # Получаем статус системы
        status = self.get_system_status()
        
        # Отображаем текущую активную модель
        if status["active_model"]:
            st.success(f"🟢 **Активная модель:** {status['active_model_name']}")
            st.caption(f"💾 Использование памяти: {status['total_memory_usage']} ГБ")
        else:
            st.warning("🟡 **Нет активной модели**")
        
        # Селектор модели
        model_options = []
        model_keys = []
        
        for model_key, model_status in status["models"].items():
            config = model_status["config"]
            
            # Формируем описание опции
            status_icon = "🟢" if model_status["is_active"] else "⚪"
            option_text = f"{status_icon} {config['display_name']} ({config['memory_gb']} ГБ)"
            
            model_options.append(option_text)
            model_keys.append(model_key)
        
        # Находим индекс активной модели
        current_index = 0
        if status["active_model"]:
            try:
                current_index = model_keys.index(status["active_model"])
            except ValueError:
                current_index = 0
        
        selected_index = st.selectbox(
            "Выберите модель:",
            range(len(model_options)),
            format_func=lambda x: model_options[x],
            index=current_index,
            help="Выбранная модель будет запущена, все остальные остановлены"
        )
        
        selected_model_key = model_keys[selected_index]
        selected_config = self.models_config[selected_model_key]
        
        # Информация о выбранной модели
        with st.expander(f"ℹ️ Информация о {selected_config['display_name']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Модель:** {selected_config['model_path']}")
                st.write(f"**Порт:** {selected_config['port']}")
                st.write(f"**Память:** {selected_config['memory_gb']} ГБ")
            
            with col2:
                st.write(f"**Время запуска:** ~{selected_config['startup_time']} сек")
                st.write(f"**Контейнер:** {selected_config['container_name']}")
            
            st.write(f"**Описание:** {selected_config['description']}")
        
        # Кнопка переключения
        if selected_model_key != status["active_model"]:
            if st.button(f"🔄 Переключиться на {selected_config['display_name']}", type="primary"):
                with st.spinner("Переключение модели..."):
                    success, message = self.start_single_container(selected_model_key)
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(message)
        else:
            st.info("✅ Выбранная модель уже активна")
        
        return selected_model_key
    
    def create_status_dashboard(self):
        """Дашборд статуса всех моделей"""
        
        st.subheader("📊 Статус всех моделей")
        
        status = self.get_system_status()
        
        for model_key, model_status in status["models"].items():
            config = model_status["config"]
            container_status = model_status["container_status"]
            
            # Определяем цвет статуса
            if model_status["is_active"]:
                status_color = "🟢"
                status_text = "АКТИВНА"
            elif container_status["running"]:
                status_color = "🟡"
                status_text = "ЗАПУЩЕНА"
            else:
                status_color = "⚪"
                status_text = "ОСТАНОВЛЕНА"
            
            with st.expander(f"{status_color} {config['display_name']} - {status_text}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Контейнер:**")
                    st.write(f"Статус: {container_status['status']}")
                    st.write(f"Health: {container_status['health']}")
                    st.write(f"Порт: {config['port']}")
                
                with col2:
                    st.write("**API:**")
                    if model_status["api_healthy"]:
                        st.write("✅ Доступен")
                    else:
                        st.write(f"❌ {model_status['api_message']}")
                    
                    st.write(f"Память: {config['memory_gb']} ГБ")
                
                with col3:
                    st.write("**Управление:**")
                    
                    if model_status["is_active"]:
                        st.success("Активная модель")
                    elif container_status["running"]:
                        if st.button(f"🛑 Остановить", key=f"stop_{model_key}"):
                            subprocess.run([
                                "docker-compose", "-f", self.compose_file,
                                "stop", config["compose_service"]
                            ])
                            st.rerun()
                    else:
                        if st.button(f"🚀 Запустить", key=f"start_{model_key}"):
                            success, message = self.start_single_container(model_key)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                            st.rerun()

def create_single_container_ui():
    """Создание полного UI для управления одиночными контейнерами"""
    
    # Инициализация менеджера
    if "single_container_manager" not in st.session_state:
        st.session_state.single_container_manager = SingleContainerManager()
    
    manager = st.session_state.single_container_manager
    
    # Заголовок
    st.title("🎯 Управление vLLM моделями")
    st.markdown("**Принцип:** Только одна модель активна одновременно")
    
    # Основной селектор модели
    selected_model = manager.create_model_selector_ui()
    
    st.divider()
    
    # Дашборд статуса
    manager.create_status_dashboard()
    
    # Кнопки управления
    st.divider()
    st.subheader("🛠️ Управление системой")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛑 Остановить все", type="secondary"):
            stopped, failed = manager.stop_all_containers()
            if stopped:
                st.success(f"Остановлены: {', '.join(stopped)}")
            if failed:
                st.error(f"Ошибки: {'; '.join(failed)}")
            st.rerun()
    
    with col2:
        if st.button("🔄 Обновить статус"):
            st.rerun()
    
    with col3:
        if st.button("📊 Экспорт статуса"):
            status = manager.get_system_status()
            st.json(status)

if __name__ == "__main__":
    # Тестирование менеджера
    manager = SingleContainerManager()
    
    print("🎯 Тестирование менеджера одиночных контейнеров")
    print("=" * 60)
    
    status = manager.get_system_status()
    print(f"Активная модель: {status['active_model_name'] or 'Нет'}")
    print(f"Использование памяти: {status['total_memory_usage']} ГБ")
    print(f"Принцип: {status['principle']}")
    
    print("\nСтатус моделей:")
    for model_key, model_status in status["models"].items():
        config = model_status["config"]
        is_active = "🟢 АКТИВНА" if model_status["is_active"] else "⚪ НЕ АКТИВНА"
        print(f"  {config['display_name']}: {is_active}")