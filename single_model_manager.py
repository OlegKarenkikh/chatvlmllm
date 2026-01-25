#!/usr/bin/env python3
"""
Менеджер для работы с одной моделью за раз
Обеспечивает корректное переключение между моделями с управлением памятью
"""

import subprocess
import time
import requests
import json
from typing import Dict, Optional, Tuple

class SingleModelManager:
    def __init__(self):
        self.models = {
            "dots-ocr": {
                "name": "dots.ocr",
                "model_path": "rednote-hilab/dots.ocr",
                "port": 8000,
                "container_name": "dots-ocr-single",
                "memory_gb": 6.0,
                "max_tokens": 1024,
                "gpu_util": 0.7
            },
            "qwen3-vl": {
                "name": "Qwen3-VL 2B",
                "model_path": "Qwen/Qwen3-VL-2B-Instruct", 
                "port": 8004,
                "container_name": "qwen3-vl-single",
                "memory_gb": 8.0,
                "max_tokens": 2048,
                "gpu_util": 0.8
            }
        }
        
        self.current_model = None
    
    def run_command(self, command, timeout=60):
        """Выполнение команды"""
        try:
            if isinstance(command, list):
                result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def check_model_health(self, port):
        """Проверка здоровья модели"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def stop_all_containers(self):
        """Остановка всех контейнеров"""
        print("🛑 Остановка всех vLLM контейнеров...")
        
        # Список всех возможных контейнеров
        containers = [
            "dots-ocr-single", "qwen3-vl-single",
            "dots-ocr-ultra-optimized", "qwen3-vl-ultra-optimized",
            "dots-ocr-vllm-optimized", "qwen-qwen3-vl-2b-instruct-vllm",
            "dots-ocr-memory-optimized", "qwen3-vl-2b-memory-optimized"
        ]
        
        for container in containers:
            success, _, _ = self.run_command(["docker", "stop", container], timeout=30)
            if success:
                print(f"✅ Остановлен: {container}")
                # Удаляем контейнер
                self.run_command(["docker", "rm", container], timeout=10)
        
        self.current_model = None
        time.sleep(3)  # Пауза для освобождения ресурсов
    
    def start_model(self, model_key: str) -> Tuple[bool, str]:
        """Запуск конкретной модели"""
        if model_key not in self.models:
            return False, f"Unknown model: {model_key}"
        
        model = self.models[model_key]
        
        print(f"🚀 Запуск {model['name']}...")
        
        # Получаем путь к кешу HuggingFace
        try:
            userprofile = subprocess.check_output(['echo', '%USERPROFILE%'], shell=True, text=True).strip()
            cache_path = f"{userprofile}/.cache/huggingface/hub"
        except:
            cache_path = "~/.cache/huggingface/hub"
        
        # Команда запуска контейнера
        command = [
            "docker", "run", "-d",
            "--name", model["container_name"],
            "--restart", "unless-stopped",
            "-p", f"{model['port']}:8000",
            "--gpus", "all",
            "--shm-size", "4g",
            "-v", f"{cache_path}:/root/.cache/huggingface/hub:rw",
            "-e", "CUDA_VISIBLE_DEVICES=0",
            "-e", "NVIDIA_VISIBLE_DEVICES=all",
            "vllm/vllm-openai:latest",
            "--model", model["model_path"],
            "--host", "0.0.0.0",
            "--port", "8000",
            "--trust-remote-code",
            "--max-model-len", str(model["max_tokens"]),
            "--gpu-memory-utilization", str(model["gpu_util"]),
            "--dtype", "bfloat16",
            "--enforce-eager",
            "--disable-log-requests"
        ]
        
        success, stdout, stderr = self.run_command(command, timeout=120)
        
        if not success:
            return False, f"Failed to start {model['name']}: {stderr}"
        
        print(f"⏳ Ожидание готовности {model['name']}...")
        
        # Ожидание готовности модели
        max_wait = 300  # 5 минут
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.check_model_health(model["port"]):
                print(f"✅ {model['name']} готов!")
                self.current_model = model_key
                return True, f"{model['name']} started successfully"
            
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0:  # Каждые 30 секунд
                print(f"⏳ Ожидание {model['name']}... ({elapsed}s)")
            
            time.sleep(5)
        
        return False, f"{model['name']} failed to start within {max_wait} seconds"
    
    def switch_to_model(self, model_key: str) -> Tuple[bool, str]:
        """Переключение на конкретную модель"""
        if model_key not in self.models:
            return False, f"Unknown model: {model_key}"
        
        model = self.models[model_key]
        
        # Если модель уже активна
        if self.current_model == model_key and self.check_model_health(model["port"]):
            return True, f"{model['name']} is already active"
        
        print(f"🔄 Переключение на {model['name']}...")
        
        # Останавливаем все контейнеры
        self.stop_all_containers()
        
        # Запускаем целевую модель
        success, message = self.start_model(model_key)
        
        if success:
            return True, f"Switched to {model['name']}"
        else:
            return False, f"Failed to switch to {model['name']}: {message}"
    
    def get_status(self) -> Dict:
        """Получение статуса системы"""
        status = {
            "current_model": self.current_model,
            "models": {}
        }
        
        for key, model in self.models.items():
            is_healthy = self.check_model_health(model["port"])
            status["models"][key] = {
                "name": model["name"],
                "port": model["port"],
                "healthy": is_healthy,
                "active": is_healthy and self.current_model == key,
                "memory_gb": model["memory_gb"]
            }
        
        return status
    
    def test_model(self, model_key: str) -> Tuple[bool, Dict]:
        """Тестирование модели"""
        if model_key not in self.models:
            return False, {"error": "Unknown model"}
        
        model = self.models[model_key]
        
        if not self.check_model_health(model["port"]):
            return False, {"error": "Model not healthy"}
        
        try:
            # Тест API моделей
            response = requests.get(f"http://localhost:{model['port']}/v1/models", timeout=10)
            
            if response.status_code == 200:
                models_data = response.json()
                return True, {
                    "healthy": True,
                    "models_api": True,
                    "available_models": [m["id"] for m in models_data.get("data", [])],
                    "port": model["port"]
                }
            else:
                return False, {"error": f"Models API returned {response.status_code}"}
                
        except Exception as e:
            return False, {"error": str(e)}

def main():
    """Основная функция для тестирования"""
    manager = SingleModelManager()
    
    print("🧪 Тестирование Single Model Manager")
    print("=" * 50)
    
    # 1. Остановка всех контейнеров
    manager.stop_all_containers()
    
    # 2. Тест запуска dots.ocr
    print("\n1️⃣ Тест запуска dots.ocr...")
    success, message = manager.switch_to_model("dots-ocr")
    
    if success:
        print(f"✅ {message}")
        
        # Тестирование API
        test_success, test_result = manager.test_model("dots-ocr")
        if test_success:
            print("✅ API dots.ocr работает корректно")
        else:
            print(f"❌ Проблема с API: {test_result}")
    else:
        print(f"❌ {message}")
    
    # 3. Статус системы
    print(f"\n2️⃣ Статус системы:")
    status = manager.get_status()
    
    print(f"Текущая модель: {status.get('current_model', 'None')}")
    for key, model_info in status["models"].items():
        status_icon = "🟢" if model_info["active"] else "🔴"
        print(f"  {status_icon} {model_info['name']}: порт {model_info['port']}, {model_info['memory_gb']} ГБ")
    
    # 4. Сохранение конфигурации
    config = {
        "single_model_mode": True,
        "current_model": manager.current_model,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models": manager.models
    }
    
    with open("single_model_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Конфигурация сохранена: single_model_config.json")
    
    # 5. Рекомендации
    print(f"\n💡 Рекомендации:")
    if manager.current_model:
        active_model = manager.models[manager.current_model]
        print(f"✅ Система готова в режиме одной модели")
        print(f"🤖 Активна: {active_model['name']} (порт {active_model['port']})")
        print(f"💡 Запуск приложения: streamlit run app.py")
        print(f"🔄 Переключение модели: python single_model_manager.py switch qwen3-vl")
    else:
        print(f"❌ Нет активной модели")
        print(f"💡 Запустите модель: python single_model_manager.py switch dots-ocr")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        manager = SingleModelManager()
        
        if action == "switch" and len(sys.argv) > 2:
            model_key = sys.argv[2]
            success, message = manager.switch_to_model(model_key)
            print(f"{'✅' if success else '❌'} {message}")
        
        elif action == "status":
            status = manager.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        
        elif action == "stop":
            manager.stop_all_containers()
            print("✅ All containers stopped")
        
        else:
            print("Usage: python single_model_manager.py [switch <model>|status|stop]")
            print("Models: dots-ocr, qwen3-vl")
    else:
        main()