#!/usr/bin/env python3
"""
Менеджер памяти для vLLM контейнеров
Управляет запуском/остановкой контейнеров для оптимизации использования GPU памяти
"""

import docker
import requests
import time
import json
import subprocess
from typing import Dict, List, Optional, Tuple
import streamlit as st

class VLLMMemoryManager:
    def __init__(self):
        self.client = docker.from_env()
        
        # Конфигурация контейнеров и их потребления памяти
        self.containers_config = {
            "dots-ocr": {
                "container_name": "dots-ocr-vllm-optimized",
                "compose_service": "dots-ocr",
                "port": 8000,
                "model": "rednote-hilab/dots.ocr",
                "estimated_memory_gb": 4.5,  # Примерное потребление памяти
                "priority": 1  # Высокий приоритет
            },
            "qwen3-vl-2b": {
                "container_name": "qwen-qwen3-vl-2b-instruct-vllm",
                "compose_service": "qwen3-vl-2b",
                "port": 8004,
                "model": "Qwen/Qwen3-VL-2B-Instruct",
                "estimated_memory_gb": 6.5,  # Примерное потребление памяти
                "priority": 2  # Средний приоритет
            },
            "qwen2-vl-2b": {
                "container_name": "qwen-qwen2-vl-2b-instruct-vllm",
                "compose_service": "qwen2-vl-2b",
                "port": 8001,
                "model": "Qwen/Qwen2-VL-2B-Instruct",
                "estimated_memory_gb": 6.0,
                "priority": 3
            }
        }
        
        self.max_gpu_memory_gb = 12  # Максимальная доступная GPU память
        self.compose_file = "docker-compose-vllm.yml"
    
    def get_container_status(self, container_name: str) -> Dict:
        """Получение статуса контейнера"""
        try:
            container = self.client.containers.get(container_name)
            return {
                "exists": True,
                "running": container.status == "running",
                "status": container.status,
                "health": getattr(container.attrs.get("State", {}), "Health", {}).get("Status", "unknown")
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
    
    def check_container_health(self, port: int) -> bool:
        """Проверка здоровья контейнера через API"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_running_containers(self) -> List[str]:
        """Получение списка запущенных контейнеров"""
        running = []
        for name, config in self.containers_config.items():
            status = self.get_container_status(config["container_name"])
            if status["running"] and self.check_container_health(config["port"]):
                running.append(name)
        return running
    
    def calculate_memory_usage(self, containers: List[str]) -> float:
        """Расчет общего потребления памяти"""
        total_memory = 0
        for container in containers:
            if container in self.containers_config:
                total_memory += self.containers_config[container]["estimated_memory_gb"]
        return total_memory
    
    def can_run_together(self, containers: List[str]) -> bool:
        """Проверка, могут ли контейнеры работать вместе"""
        total_memory = self.calculate_memory_usage(containers)
        return total_memory <= self.max_gpu_memory_gb
    
    def start_container(self, container_name: str) -> bool:
        """Запуск контейнера"""
        if container_name not in self.containers_config:
            return False
        
        config = self.containers_config[container_name]
        
        try:
            # Используем docker-compose для запуска
            result = subprocess.run([
                "docker-compose", "-f", self.compose_file,
                "up", "-d", config["compose_service"]
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Ждем готовности контейнера
                max_wait = 120  # 2 минуты
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    if self.check_container_health(config["port"]):
                        return True
                    time.sleep(5)
                
                return False
            else:
                print(f"Ошибка запуска {container_name}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Ошибка запуска {container_name}: {e}")
            return False
    
    def stop_container(self, container_name: str) -> bool:
        """Остановка контейнера"""
        if container_name not in self.containers_config:
            return False
        
        config = self.containers_config[container_name]
        
        try:
            # Используем docker-compose для остановки
            result = subprocess.run([
                "docker-compose", "-f", self.compose_file,
                "stop", config["compose_service"]
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Ошибка остановки {container_name}: {e}")
            return False
    
    def switch_to_model(self, target_model: str) -> Tuple[bool, str]:
        """Переключение на конкретную модель с управлением памятью"""
        
        # Находим контейнер для целевой модели
        target_container = None
        for name, config in self.containers_config.items():
            if config["model"] == target_model:
                target_container = name
                break
        
        if not target_container:
            return False, f"Модель {target_model} не найдена в конфигурации"
        
        running_containers = self.get_running_containers()
        target_config = self.containers_config[target_container]
        
        # Если целевой контейнер уже запущен и здоров
        if target_container in running_containers:
            return True, f"Модель {target_model} уже активна"
        
        # Проверяем, можем ли запустить целевой контейнер с текущими
        potential_containers = running_containers + [target_container]
        
        if self.can_run_together(potential_containers):
            # Можем запустить без остановки других
            success = self.start_container(target_container)
            if success:
                return True, f"Модель {target_model} запущена (параллельно с другими)"
            else:
                return False, f"Ошибка запуска модели {target_model}"
        else:
            # Нужно освободить память - останавливаем контейнеры с низким приоритетом
            containers_to_stop = []
            
            # Сортируем по приоритету (высокий приоритет = меньшее число)
            running_sorted = sorted(running_containers, 
                                  key=lambda x: self.containers_config[x]["priority"], 
                                  reverse=True)
            
            memory_needed = target_config["estimated_memory_gb"]
            current_memory = self.calculate_memory_usage(running_containers)
            
            for container in running_sorted:
                if current_memory + memory_needed <= self.max_gpu_memory_gb:
                    break
                
                containers_to_stop.append(container)
                current_memory -= self.containers_config[container]["estimated_memory_gb"]
            
            # Останавливаем контейнеры
            stopped_containers = []
            for container in containers_to_stop:
                if self.stop_container(container):
                    stopped_containers.append(container)
                    time.sleep(2)  # Небольшая пауза между остановками
            
            # Запускаем целевой контейнер
            success = self.start_container(target_container)
            
            if success:
                message = f"Модель {target_model} запущена"
                if stopped_containers:
                    stopped_models = [self.containers_config[c]["model"].split("/")[-1] for c in stopped_containers]
                    message += f" (остановлены: {', '.join(stopped_models)})"
                return True, message
            else:
                # Если не удалось запустить, пытаемся восстановить остановленные
                for container in stopped_containers:
                    self.start_container(container)
                return False, f"Ошибка запуска модели {target_model}"
    
    def get_memory_status(self) -> Dict:
        """Получение статуса использования памяти"""
        running_containers = self.get_running_containers()
        current_memory = self.calculate_memory_usage(running_containers)
        
        container_details = []
        for container in running_containers:
            config = self.containers_config[container]
            container_details.append({
                "name": container,
                "model": config["model"].split("/")[-1],
                "memory_gb": config["estimated_memory_gb"],
                "port": config["port"],
                "priority": config["priority"]
            })
        
        return {
            "running_containers": len(running_containers),
            "current_memory_gb": current_memory,
            "max_memory_gb": self.max_gpu_memory_gb,
            "available_memory_gb": self.max_gpu_memory_gb - current_memory,
            "memory_usage_percent": (current_memory / self.max_gpu_memory_gb) * 100,
            "containers": container_details,
            "can_add_more": current_memory < self.max_gpu_memory_gb
        }
    
    def optimize_memory_usage(self) -> Tuple[bool, str]:
        """Оптимизация использования памяти"""
        running_containers = self.get_running_containers()
        current_memory = self.calculate_memory_usage(running_containers)
        
        if current_memory <= self.max_gpu_memory_gb:
            return True, f"Память в норме: {current_memory:.1f}/{self.max_gpu_memory_gb} ГБ"
        
        # Превышение лимита - останавливаем контейнеры с низким приоритетом
        containers_sorted = sorted(running_containers, 
                                 key=lambda x: self.containers_config[x]["priority"], 
                                 reverse=True)
        
        stopped_containers = []
        for container in containers_sorted:
            if current_memory <= self.max_gpu_memory_gb:
                break
            
            if self.stop_container(container):
                stopped_containers.append(container)
                current_memory -= self.containers_config[container]["estimated_memory_gb"]
                time.sleep(2)
        
        if stopped_containers:
            stopped_models = [self.containers_config[c]["model"].split("/")[-1] for c in stopped_containers]
            return True, f"Оптимизировано: остановлены {', '.join(stopped_models)}"
        else:
            return False, "Не удалось оптимизировать память"

def create_memory_management_ui():
    """Создание UI для управления памятью vLLM контейнеров"""
    
    st.subheader("🧠 Управление памятью vLLM")
    
    # Инициализация менеджера
    if "memory_manager" not in st.session_state:
        st.session_state.memory_manager = VLLMMemoryManager()
    
    manager = st.session_state.memory_manager
    
    # Получение статуса памяти
    memory_status = manager.get_memory_status()
    
    # Отображение статуса памяти
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Активных контейнеров", 
            memory_status["running_containers"],
            help="Количество запущенных vLLM контейнеров"
        )
    
    with col2:
        st.metric(
            "Использование GPU", 
            f"{memory_status['current_memory_gb']:.1f} ГБ",
            f"{memory_status['memory_usage_percent']:.1f}%"
        )
    
    with col3:
        st.metric(
            "Доступно памяти", 
            f"{memory_status['available_memory_gb']:.1f} ГБ",
            help="Свободная GPU память"
        )
    
    with col4:
        memory_color = "normal"
        if memory_status['memory_usage_percent'] > 90:
            memory_color = "inverse"
        elif memory_status['memory_usage_percent'] > 75:
            memory_color = "off"
        
        st.metric(
            "Лимит памяти", 
            f"{memory_status['max_memory_gb']} ГБ",
            help="Максимальная доступная GPU память"
        )
    
    # Прогресс-бар использования памяти
    progress_value = min(memory_status['memory_usage_percent'] / 100, 1.0)
    st.progress(progress_value, text=f"Использование GPU памяти: {memory_status['memory_usage_percent']:.1f}%")
    
    # Предупреждения
    if memory_status['memory_usage_percent'] > 100:
        st.error("⚠️ Превышен лимит GPU памяти! Некоторые контейнеры могут работать нестабильно.")
    elif memory_status['memory_usage_percent'] > 90:
        st.warning("⚠️ Высокое использование GPU памяти. Рекомендуется оптимизация.")
    
    # Детали активных контейнеров
    if memory_status["containers"]:
        st.subheader("📊 Активные контейнеры")
        
        for container in memory_status["containers"]:
            with st.expander(f"🤖 {container['model']} (Порт: {container['port']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Память:** {container['memory_gb']} ГБ")
                
                with col2:
                    st.write(f"**Приоритет:** {container['priority']}")
                
                with col3:
                    if st.button(f"Остановить {container['model']}", key=f"stop_{container['name']}"):
                        success = manager.stop_container(container['name'])
                        if success:
                            st.success(f"Контейнер {container['model']} остановлен")
                            st.rerun()
                        else:
                            st.error(f"Ошибка остановки {container['model']}")
    
    # Управление контейнерами
    st.subheader("🎛️ Управление контейнерами")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔧 Оптимизировать память", type="primary"):
            success, message = manager.optimize_memory_usage()
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()
    
    with col2:
        if st.button("🔄 Обновить статус"):
            st.rerun()
    
    # Быстрое переключение моделей
    st.subheader("🚀 Быстрое переключение моделей")
    
    available_models = [
        "rednote-hilab/dots.ocr",
        "Qwen/Qwen3-VL-2B-Instruct",
        "Qwen/Qwen2-VL-2B-Instruct"
    ]
    
    selected_model = st.selectbox(
        "Выберите модель для активации",
        available_models,
        help="Система автоматически управляет памятью при переключении"
    )
    
    if st.button("🎯 Переключиться на модель", type="secondary"):
        with st.spinner(f"Переключение на {selected_model.split('/')[-1]}..."):
            success, message = manager.switch_to_model(selected_model)
            
            if success:
                st.success(message)
            else:
                st.error(message)
            
            time.sleep(2)
            st.rerun()
    
    # Экспорт статуса
    with st.expander("📋 Экспорт статуса"):
        status_json = json.dumps(memory_status, indent=2, ensure_ascii=False)
        st.code(status_json, language="json")
        
        st.download_button(
            "💾 Скачать статус",
            data=status_json,
            file_name=f"vllm_memory_status_{int(time.time())}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    # Тестирование менеджера памяти
    manager = VLLMMemoryManager()
    
    print("🧠 Тестирование менеджера памяти vLLM")
    print("=" * 50)
    
    # Статус памяти
    status = manager.get_memory_status()
    print(f"Активных контейнеров: {status['running_containers']}")
    print(f"Использование памяти: {status['current_memory_gb']:.1f}/{status['max_memory_gb']} ГБ ({status['memory_usage_percent']:.1f}%)")
    
    for container in status['containers']:
        print(f"  - {container['model']}: {container['memory_gb']} ГБ (порт {container['port']})")
    
    # Тест переключения модели
    print(f"\n🔄 Тест переключения на Qwen3-VL...")
    success, message = manager.switch_to_model("Qwen/Qwen3-VL-2B-Instruct")
    print(f"Результат: {message}")