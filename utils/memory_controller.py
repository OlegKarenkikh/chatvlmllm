#!/usr/bin/env python3
"""
Контроллер памяти для управления переключением между vLLM и Transformers
Обеспечивает контроль выгрузки и загрузки моделей с управлением памятью
"""

import gc
import time
import psutil
import subprocess
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import threading
import logging

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionMode(Enum):
    """Режимы выполнения"""
    VLLM = "vllm"
    TRANSFORMERS = "transformers"

@dataclass
class MemoryInfo:
    """Информация о памяти"""
    total_gb: float
    used_gb: float
    free_gb: float
    utilization_percent: float

@dataclass
class ModelInfo:
    """Информация о модели"""
    name: str
    mode: ExecutionMode
    memory_usage_gb: float
    is_loaded: bool
    container_id: Optional[str] = None
    process_id: Optional[int] = None

class MemoryController:
    """Контроллер памяти для управления моделями"""
    
    def __init__(self):
        self.current_mode = None
        self.loaded_models: Dict[str, ModelInfo] = {}
        self.vllm_containers: Dict[str, str] = {}  # model_name -> container_id
        self.transformers_models: Dict[str, Any] = {}  # model_name -> model_instance
        self.memory_threshold_gb = 2.0  # Минимальный резерв памяти
        self.cleanup_lock = threading.Lock()
        
    def get_gpu_memory_info(self) -> MemoryInfo:
        """Получение информации о GPU памяти"""
        if not TORCH_AVAILABLE or not torch.cuda.is_available():
            return MemoryInfo(0, 0, 0, 0)
        
        try:
            # Используем nvidia-smi для точной информации
            result = subprocess.run([
                "nvidia-smi", 
                "--query-gpu=memory.total,memory.used,memory.free",
                "--format=csv,noheader,nounits"
            ], capture_output=True, text=True, check=True)
            
            line = result.stdout.strip().split('\n')[0]
            total_mb, used_mb, free_mb = map(int, line.split(', '))
            
            total_gb = total_mb / 1024
            used_gb = used_mb / 1024
            free_gb = free_mb / 1024
            utilization = (used_gb / total_gb) * 100
            
            return MemoryInfo(total_gb, used_gb, free_gb, utilization)
            
        except Exception as e:
            logger.warning(f"Ошибка получения GPU памяти: {e}")
            # Fallback на PyTorch
            try:
                props = torch.cuda.get_device_properties(0)
                total_gb = props.total_memory / (1024 ** 3)
                allocated_gb = torch.cuda.memory_allocated(0) / (1024 ** 3)
                reserved_gb = torch.cuda.memory_reserved(0) / (1024 ** 3)
                free_gb = total_gb - reserved_gb
                utilization = (reserved_gb / total_gb) * 100
                
                return MemoryInfo(total_gb, reserved_gb, free_gb, utilization)
            except:
                return MemoryInfo(0, 0, 0, 0)
    
    def get_system_memory_info(self) -> MemoryInfo:
        """Получение информации о системной памяти"""
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024 ** 3)
        used_gb = memory.used / (1024 ** 3)
        free_gb = memory.available / (1024 ** 3)
        utilization = memory.percent
        
        return MemoryInfo(total_gb, used_gb, free_gb, utilization)
    
    def cleanup_gpu_memory(self, force: bool = False) -> bool:
        """Очистка GPU памяти"""
        with self.cleanup_lock:
            try:
                logger.info("🧹 Очистка GPU памяти...")
                
                if TORCH_AVAILABLE and torch.cuda.is_available():
                    # Очистка кеша всех GPU
                    for i in range(torch.cuda.device_count()):
                        with torch.cuda.device(i):
                            torch.cuda.empty_cache()
                            torch.cuda.synchronize()
                    
                    # IPC очистка
                    try:
                        torch.cuda.ipc_collect()
                    except:
                        pass
                
                # Принудительная сборка мусора
                for _ in range(3):
                    gc.collect()
                    time.sleep(0.1)
                
                logger.info("✅ GPU память очищена")
                return True
                
            except Exception as e:
                logger.error(f"❌ Ошибка очистки GPU памяти: {e}")
                return False
    
    def kill_gpu_processes(self, exclude_pids: List[int] = None) -> List[Dict]:
        """Завершение процессов, использующих GPU"""
        if exclude_pids is None:
            exclude_pids = []
        
        killed_processes = []
        
        try:
            result = subprocess.run([
                "nvidia-smi", 
                "--query-compute-apps=pid,process_name,used_memory",
                "--format=csv,noheader,nounits"
            ], capture_output=True, text=True, check=True)
            
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    pid = int(parts[0])
                    name = parts[1]
                    memory_mb = int(parts[2])
                    
                    if pid in exclude_pids:
                        continue
                    
                    try:
                        if psutil.pid_exists(pid):
                            process = psutil.Process(pid)
                            logger.info(f"🔪 Завершение процесса: {name} (PID: {pid}, {memory_mb} MB)")
                            
                            process.terminate()
                            time.sleep(1)
                            
                            if process.is_running():
                                process.kill()
                                time.sleep(0.5)
                            
                            killed_processes.append({
                                'pid': pid,
                                'name': name,
                                'memory_mb': memory_mb
                            })
                    except Exception as e:
                        logger.warning(f"Не удалось завершить процесс {pid}: {e}")
        
        except Exception as e:
            logger.warning(f"Ошибка получения GPU процессов: {e}")
        
        return killed_processes
    
    def check_memory_availability(self, required_gb: float) -> Tuple[bool, str]:
        """Проверка доступности памяти"""
        gpu_info = self.get_gpu_memory_info()
        
        if gpu_info.free_gb < required_gb:
            return False, f"Недостаточно GPU памяти: требуется {required_gb:.1f}GB, доступно {gpu_info.free_gb:.1f}GB"
        
        if gpu_info.free_gb < (required_gb + self.memory_threshold_gb):
            return False, f"Недостаточно резерва памяти: требуется {required_gb + self.memory_threshold_gb:.1f}GB, доступно {gpu_info.free_gb:.1f}GB"
        
        return True, f"Достаточно памяти: {gpu_info.free_gb:.1f}GB доступно"
    
    def get_vllm_containers(self) -> Dict[str, str]:
        """Получение списка vLLM контейнеров"""
        containers = {}
        
        try:
            result = subprocess.run([
                "docker", "ps", "--format", "{{.ID}}\t{{.Names}}\t{{.Image}}"
            ], capture_output=True, text=True, check=True)
            
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 3:
                    container_id, name, image = parts
                    
                    # Определяем vLLM контейнеры по образу или имени
                    if 'vllm' in image.lower() or 'vllm' in name.lower():
                        containers[name] = container_id
        
        except Exception as e:
            logger.warning(f"Ошибка получения Docker контейнеров: {e}")
        
        return containers
    
    def stop_vllm_containers(self, model_names: List[str] = None) -> List[str]:
        """Остановка vLLM контейнеров"""
        stopped_containers = []
        containers = self.get_vllm_containers()
        
        for name, container_id in containers.items():
            # Если указаны конкретные модели, проверяем соответствие
            if model_names and not any(model in name for model in model_names):
                continue
            
            try:
                logger.info(f"🛑 Остановка vLLM контейнера: {name}")
                subprocess.run(["docker", "stop", container_id], check=True, capture_output=True)
                stopped_containers.append(name)
                
                # Удаляем из отслеживания
                if name in self.vllm_containers:
                    del self.vllm_containers[name]
                
            except Exception as e:
                logger.error(f"Ошибка остановки контейнера {name}: {e}")
        
        return stopped_containers
    
    def unload_transformers_models(self, model_names: List[str] = None) -> List[str]:
        """Выгрузка Transformers моделей"""
        unloaded_models = []
        
        # Используем ModelLoader для выгрузки
        try:
            from models.model_loader import ModelLoader
            
            loaded_models = ModelLoader.get_loaded_models()
            
            for model_name in loaded_models:
                # Если указаны конкретные модели, проверяем соответствие
                if model_names and model_name not in model_names:
                    continue
                
                logger.info(f"📤 Выгрузка Transformers модели: {model_name}")
                
                if ModelLoader.unload_model(model_name):
                    unloaded_models.append(model_name)
                    
                    # Удаляем из отслеживания
                    if model_name in self.transformers_models:
                        del self.transformers_models[model_name]
        
        except Exception as e:
            logger.error(f"Ошибка выгрузки Transformers моделей: {e}")
        
        return unloaded_models
    
    def switch_to_vllm_mode(self, target_model: str = None) -> Tuple[bool, str]:
        """Переключение в режим vLLM"""
        logger.info(f"🔄 Переключение в режим vLLM (модель: {target_model})")
        
        try:
            # 1. Выгружаем все Transformers модели
            unloaded_transformers = self.unload_transformers_models()
            if unloaded_transformers:
                logger.info(f"📤 Выгружены Transformers модели: {unloaded_transformers}")
            
            # 2. Очищаем GPU память
            self.cleanup_gpu_memory()
            
            # 3. Проверяем доступность памяти для vLLM
            required_memory = 8.0  # Примерная потребность vLLM
            can_load, message = self.check_memory_availability(required_memory)
            
            if not can_load:
                # Принудительная очистка
                logger.warning("⚠️ Недостаточно памяти, принудительная очистка...")
                self.kill_gpu_processes()
                self.cleanup_gpu_memory()
                
                # Повторная проверка
                can_load, message = self.check_memory_availability(required_memory)
                if not can_load:
                    return False, f"Не удалось освободить память для vLLM: {message}"
            
            # 4. Останавливаем другие vLLM контейнеры (если нужно переключить модель)
            if target_model:
                current_containers = self.get_vllm_containers()
                other_models = [name for name in current_containers.keys() 
                              if target_model not in name]
                
                if other_models:
                    stopped = self.stop_vllm_containers(other_models)
                    logger.info(f"🛑 Остановлены контейнеры других моделей: {stopped}")
            
            self.current_mode = ExecutionMode.VLLM
            
            gpu_info = self.get_gpu_memory_info()
            return True, f"Переключение в vLLM режим успешно. Доступно {gpu_info.free_gb:.1f}GB GPU памяти"
            
        except Exception as e:
            logger.error(f"❌ Ошибка переключения в vLLM режим: {e}")
            return False, str(e)
    
    def switch_to_transformers_mode(self, target_model: str = None) -> Tuple[bool, str]:
        """Переключение в режим Transformers"""
        logger.info(f"🔄 Переключение в режим Transformers (модель: {target_model})")
        
        try:
            # 1. Останавливаем все vLLM контейнеры
            stopped_containers = self.stop_vllm_containers()
            if stopped_containers:
                logger.info(f"🛑 Остановлены vLLM контейнеры: {stopped_containers}")
            
            # 2. Очищаем GPU память
            self.cleanup_gpu_memory()
            
            # 3. Выгружаем другие Transformers модели (если нужно переключить модель)
            if target_model:
                try:
                    from models.model_loader import ModelLoader
                    loaded_models = ModelLoader.get_loaded_models()
                    other_models = [name for name in loaded_models if name != target_model]
                    
                    if other_models:
                        unloaded = self.unload_transformers_models(other_models)
                        logger.info(f"📤 Выгружены другие модели: {unloaded}")
                except:
                    pass
            
            # 4. Проверяем доступность памяти для Transformers
            required_memory = 4.0  # Примерная потребность Transformers
            can_load, message = self.check_memory_availability(required_memory)
            
            if not can_load:
                # Принудительная очистка
                logger.warning("⚠️ Недостаточно памяти, принудительная очистка...")
                self.kill_gpu_processes()
                self.cleanup_gpu_memory()
                
                # Повторная проверка
                can_load, message = self.check_memory_availability(required_memory)
                if not can_load:
                    return False, f"Не удалось освободить память для Transformers: {message}"
            
            self.current_mode = ExecutionMode.TRANSFORMERS
            
            gpu_info = self.get_gpu_memory_info()
            return True, f"Переключение в Transformers режим успешно. Доступно {gpu_info.free_gb:.1f}GB GPU памяти"
            
        except Exception as e:
            logger.error(f"❌ Ошибка переключения в Transformers режим: {e}")
            return False, str(e)
    
    def change_model_in_container(self, new_model: str, container_type: str = "vllm") -> Tuple[bool, str]:
        """Смена модели в контейнере с контролем памяти"""
        logger.info(f"🔄 Смена модели на {new_model} в {container_type}")
        
        try:
            if container_type == "vllm":
                # Для vLLM нужно пересоздать контейнер с новой моделью
                
                # 1. Останавливаем текущие контейнеры
                stopped = self.stop_vllm_containers()
                logger.info(f"🛑 Остановлены контейнеры: {stopped}")
                
                # 2. Очищаем память
                self.cleanup_gpu_memory()
                
                # 3. Проверяем кеш модели
                try:
                    from models.model_loader import ModelLoader
                    is_cached, cache_msg = ModelLoader.check_model_cache(new_model)
                    
                    if not is_cached:
                        return False, f"Модель {new_model} не найдена в кеше: {cache_msg}"
                    
                    logger.info(f"✅ Модель {new_model} найдена в кеше")
                except Exception as e:
                    logger.warning(f"Не удалось проверить кеш модели: {e}")
                
                # 4. Проверяем память
                required_memory = 8.0
                can_load, message = self.check_memory_availability(required_memory)
                
                if not can_load:
                    return False, f"Недостаточно памяти для загрузки {new_model}: {message}"
                
                # 5. Запускаем новый контейнер (это должно делаться внешним кодом)
                return True, f"Готов к запуску {new_model} в vLLM контейнере"
                
            else:  # transformers
                # Для Transformers выгружаем текущую и загружаем новую
                
                # 1. Выгружаем все модели
                unloaded = self.unload_transformers_models()
                logger.info(f"📤 Выгружены модели: {unloaded}")
                
                # 2. Очищаем память
                self.cleanup_gpu_memory()
                
                # 3. Проверяем кеш новой модели
                try:
                    from models.model_loader import ModelLoader
                    is_cached, cache_msg = ModelLoader.check_model_cache(new_model)
                    
                    if not is_cached:
                        return False, f"Модель {new_model} не найдена в кеше: {cache_msg}"
                    
                    logger.info(f"✅ Модель {new_model} найдена в кеше")
                except Exception as e:
                    return False, f"Ошибка проверки кеша модели: {e}"
                
                # 4. Проверяем память
                required_memory = 4.0
                can_load, message = self.check_memory_availability(required_memory)
                
                if not can_load:
                    return False, f"Недостаточно памяти для загрузки {new_model}: {message}"
                
                # 5. Загружаем новую модель
                try:
                    from models.model_loader import ModelLoader
                    model = ModelLoader.load_model(new_model)
                    self.transformers_models[new_model] = model
                    
                    gpu_info = self.get_gpu_memory_info()
                    return True, f"Модель {new_model} успешно загружена. Использовано {gpu_info.used_gb:.1f}GB GPU памяти"
                    
                except Exception as e:
                    return False, f"Ошибка загрузки модели {new_model}: {e}"
        
        except Exception as e:
            logger.error(f"❌ Ошибка смены модели: {e}")
            return False, str(e)
    
    def get_cached_models(self) -> List[str]:
        """Получение списка кешированных моделей"""
        cached_models = []
        
        try:
            from models.model_loader import ModelLoader
            config = ModelLoader.load_config()
            
            for model_key in config.get("models", {}).keys():
                is_cached, _ = ModelLoader.check_model_cache(model_key)
                if is_cached:
                    cached_models.append(model_key)
        
        except Exception as e:
            logger.error(f"Ошибка получения кешированных моделей: {e}")
        
        return cached_models
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Получение полного статуса памяти"""
        gpu_info = self.get_gpu_memory_info()
        system_info = self.get_system_memory_info()
        
        return {
            "current_mode": self.current_mode.value if self.current_mode else None,
            "gpu_memory": {
                "total_gb": gpu_info.total_gb,
                "used_gb": gpu_info.used_gb,
                "free_gb": gpu_info.free_gb,
                "utilization_percent": gpu_info.utilization_percent
            },
            "system_memory": {
                "total_gb": system_info.total_gb,
                "used_gb": system_info.used_gb,
                "free_gb": system_info.free_gb,
                "utilization_percent": system_info.utilization_percent
            },
            "loaded_models": {
                "transformers": list(self.transformers_models.keys()),
                "vllm_containers": list(self.vllm_containers.keys())
            },
            "cached_models": self.get_cached_models(),
            "memory_threshold_gb": self.memory_threshold_gb
        }
    
    def emergency_cleanup(self) -> Tuple[bool, str]:
        """Экстренная очистка всех ресурсов"""
        logger.warning("🚨 Экстренная очистка памяти...")
        
        try:
            # 1. Останавливаем все vLLM контейнеры
            stopped_containers = self.stop_vllm_containers()
            
            # 2. Выгружаем все Transformers модели
            unloaded_models = self.unload_transformers_models()
            
            # 3. Завершаем GPU процессы
            killed_processes = self.kill_gpu_processes()
            
            # 4. Очищаем GPU память
            self.cleanup_gpu_memory()
            
            # 5. Очищаем отслеживание
            self.vllm_containers.clear()
            self.transformers_models.clear()
            self.current_mode = None
            
            gpu_info = self.get_gpu_memory_info()
            
            summary = f"""Экстренная очистка завершена:
- Остановлено vLLM контейнеров: {len(stopped_containers)}
- Выгружено Transformers моделей: {len(unloaded_models)}
- Завершено GPU процессов: {len(killed_processes)}
- Доступно GPU памяти: {gpu_info.free_gb:.1f}GB"""
            
            logger.info("✅ " + summary.replace('\n', ' '))
            return True, summary
            
        except Exception as e:
            error_msg = f"Ошибка экстренной очистки: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg

# Глобальный экземпляр контроллера
memory_controller = MemoryController()