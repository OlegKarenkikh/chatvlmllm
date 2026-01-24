#!/usr/bin/env python3
"""
Селектор режима работы моделей:
1. Transformers режим (8-bit квантизация, низкое потребление памяти)
2. vLLM режим (высокая производительность, больше памяти)

С правильным монтированием кешей моделей
"""

import os
import subprocess
import json
import time
import requests
from pathlib import Path

class ModelModeSelector:
    def __init__(self):
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        self.models_config = self.load_models_config()
        self.current_mode = None
        self.running_containers = []
        
    def load_models_config(self):
        """Загрузка конфигурации моделей"""
        config = {
            "transformers_models": {
                "rednote-hilab/dots.ocr": {
                    "name": "DotsOCR",
                    "size_gb": 5.67,
                    "memory_8bit_gb": 3.5,
                    "category": "ocr",
                    "priority": 1
                },
                "stepfun-ai/GOT-OCR-2.0-hf": {
                    "name": "GOT-OCR 2.0",
                    "size_gb": 1.06,
                    "memory_8bit_gb": 0.8,
                    "category": "ocr",
                    "priority": 2
                },
                "Qwen/Qwen2-VL-2B-Instruct": {
                    "name": "Qwen2-VL 2B",
                    "size_gb": 4.13,
                    "memory_8bit_gb": 2.5,
                    "category": "vlm",
                    "priority": 3
                },
                "microsoft/Phi-3.5-vision-instruct": {
                    "name": "Phi-3.5 Vision",
                    "size_gb": 7.73,
                    "memory_8bit_gb": 4.5,
                    "category": "vlm",
                    "priority": 4
                }
            },
            "vllm_models": {
                "rednote-hilab/dots.ocr": {
                    "name": "DotsOCR",
                    "container_name": "dots-ocr-vllm",
                    "port": 8000,
                    "size_gb": 5.67,
                    "memory_required_gb": 8.0,
                    "category": "ocr",
                    "vllm_params": {
                        "max_model_len": 2048,
                        "gpu_memory_utilization": 0.7,
                        "trust_remote_code": True,
                        "enforce_eager": True,
                        "dtype": "bfloat16"
                    },
                    "priority": 1
                },
                "Qwen/Qwen2-VL-2B-Instruct": {
                    "name": "Qwen2-VL 2B",
                    "container_name": "qwen2-vl-2b-vllm",
                    "port": 8001,
                    "size_gb": 4.13,
                    "memory_required_gb": 6.0,
                    "category": "vlm",
                    "vllm_params": {
                        "max_model_len": 4096,
                        "gpu_memory_utilization": 0.6,
                        "trust_remote_code": True,
                        "enforce_eager": False,
                        "dtype": "bfloat16"
                    },
                    "priority": 2
                },
                "stepfun-ai/GOT-OCR-2.0-hf": {
                    "name": "GOT-OCR 2.0",
                    "container_name": "got-ocr-vllm",
                    "port": 8002,
                    "size_gb": 1.06,
                    "memory_required_gb": 3.0,
                    "category": "ocr",
                    "vllm_params": {
                        "max_model_len": 2048,
                        "gpu_memory_utilization": 0.5,
                        "trust_remote_code": True,
                        "enforce_eager": True,
                        "dtype": "bfloat16"
                    },
                    "priority": 3
                }
            }
        }
        return config
    
    def get_gpu_info(self):
        """Получение информации о GPU"""
        try:
            result = subprocess.run([
                "nvidia-smi", 
                "--query-gpu=memory.total,memory.free,memory.used",
                "--format=csv,noheader,nounits"
            ], capture_output=True, text=True, check=True)
            
            total, free, used = map(int, result.stdout.strip().split(', '))
            return {
                'total_mb': total,
                'free_mb': free,
                'used_mb': used,
                'total_gb': total / 1024,
                'free_gb': free / 1024,
                'used_gb': used / 1024
            }
        except Exception as e:
            print(f"❌ Ошибка получения GPU информации: {e}")
            return None
    
    def check_cache_dir(self):
        """Проверка и создание директории кеша"""
        print(f"📁 Проверка кеш директории: {self.cache_dir}")
        
        if not self.cache_dir.exists():
            print("📁 Создание кеш директории...")
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Проверка прав доступа
        if not os.access(self.cache_dir, os.R_OK | os.W_OK):
            print("⚠️ Недостаточно прав для кеш директории")
            return False
        
        # Проверка существующих моделей
        cached_models = []
        for item in self.cache_dir.iterdir():
            if item.is_dir() and item.name.startswith('models--'):
                model_name = item.name.replace('models--', '').replace('--', '/')
                cached_models.append(model_name)
        
        if cached_models:
            print(f"✅ Найдено {len(cached_models)} кешированных моделей:")
            for model in cached_models:
                print(f"   • {model}")
        else:
            print("📥 Кеш пуст, модели будут загружены при первом использовании")
        
        return True
    
    def recommend_mode(self):
        """Рекомендация режима работы на основе доступной памяти"""
        gpu_info = self.get_gpu_info()
        if not gpu_info:
            return "transformers", "Не удалось определить GPU память"
        
        free_gb = gpu_info['free_gb']
        total_gb = gpu_info['total_gb']
        
        print(f"📊 GPU память: {free_gb:.1f} GB свободно из {total_gb:.1f} GB")
        
        if free_gb >= 8:
            return "vllm", f"Достаточно памяти для vLLM режима ({free_gb:.1f} GB свободно)"
        elif free_gb >= 4:
            return "transformers", f"Рекомендуется Transformers режим ({free_gb:.1f} GB свободно)"
        else:
            return "transformers", f"Только Transformers режим возможен ({free_gb:.1f} GB свободно)"
    
    def start_transformers_mode(self, model_name=None):
        """Запуск Transformers режима"""
        if not model_name:
            # Выбор модели по умолчанию
            model_name = "rednote-hilab/dots.ocr"
        
        print(f"🚀 Запуск Transformers режима с моделью: {model_name}")
        
        # Создание скрипта запуска
        script_content = f'''#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dots_ocr_transformers_8bit import DotsOCRTransformers, app
import threading

def load_model():
    ocr_model = DotsOCRTransformers()
    ocr_model.model_name = "{model_name}"
    ocr_model.load_model()
    app.ocr_model = ocr_model

if __name__ == "__main__":
    print("🚀 Запуск Transformers режима")
    print(f"📦 Модель: {model_name}")
    print(f"📁 Кеш: {os.path.expanduser('~/.cache/huggingface/hub')}")
    
    # Загрузка модели в фоне
    model_thread = threading.Thread(target=load_model)
    model_thread.daemon = True
    model_thread.start()
    
    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=8000, debug=False)
'''
        
        with open("run_transformers_mode.py", "w", encoding="utf-8") as f:
            f.write(script_content)
        
        print("✅ Transformers режим настроен")
        print("🌐 Запуск сервера на порту 8000...")
        print("📡 API: http://localhost:8000")
        
        self.current_mode = "transformers"
        return True
    
    def start_vllm_mode(self, models=None):
        """Запуск vLLM режима с монтированием кешей"""
        if not models:
            models = ["rednote-hilab/dots.ocr"]
        
        print(f"🚀 Запуск vLLM режима с моделями: {', '.join(models)}")
        
        # Остановка существующих контейнеров
        self.stop_all_containers()
        
        # Подготовка путей для монтирования
        cache_path = str(self.cache_dir).replace('\\', '/')
        
        started_containers = []
        
        for model_name in models:
            if model_name not in self.models_config["vllm_models"]:
                print(f"⚠️ Модель {model_name} не поддерживается в vLLM режиме")
                continue
            
            model_config = self.models_config["vllm_models"][model_name]
            container_name = model_config["container_name"]
            port = model_config["port"]
            vllm_params = model_config["vllm_params"]
            
            print(f"🔄 Запуск контейнера для {model_config['name']}...")
            
            # Формирование команды Docker
            docker_cmd = [
                "docker", "run", "-d",
                "--gpus", "all",
                "--name", container_name,
                "--restart", "unless-stopped",
                "-p", f"{port}:8000",
                # КРИТИЧНО: Монтирование кеша с правами на чтение и запись
                "-v", f"{cache_path}:/root/.cache/huggingface/hub",
                # Дополнительные монтирования для полного доступа
                "-v", f"{cache_path}:/home/vllm/.cache/huggingface/hub",
                "--shm-size=8g",
                # Переменные окружения для кеша
                "-e", f"HF_HOME=/root/.cache/huggingface",
                "-e", f"TRANSFORMERS_CACHE=/root/.cache/huggingface/hub",
                "-e", f"HF_HUB_CACHE=/root/.cache/huggingface/hub",
                # Образ vLLM
                "vllm/vllm-openai:latest",
                # Параметры vLLM
                "--model", model_name,
                "--host", "0.0.0.0",
                "--port", "8000",
                "--trust-remote-code",
                "--max-model-len", str(vllm_params["max_model_len"]),
                "--gpu-memory-utilization", str(vllm_params["gpu_memory_utilization"]),
                "--dtype", vllm_params["dtype"],
                "--disable-log-requests"
            ]
            
            if vllm_params["enforce_eager"]:
                docker_cmd.append("--enforce-eager")
            
            try:
                result = subprocess.run(docker_cmd, check=True, capture_output=True, text=True)
                print(f"✅ Контейнер {container_name} запущен на порту {port}")
                started_containers.append({
                    "name": container_name,
                    "model": model_name,
                    "port": port,
                    "config": model_config
                })
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка запуска {container_name}: {e}")
                print(f"❌ Stderr: {e.stderr}")
        
        if started_containers:
            self.running_containers = started_containers
            self.current_mode = "vllm"
            
            print(f"\n🎉 vLLM режим запущен с {len(started_containers)} контейнерами:")
            for container in started_containers:
                print(f"   • {container['config']['name']}: http://localhost:{container['port']}")
            
            print(f"\n📁 Кеш моделей примонтирован: {cache_path}")
            print("💾 Контейнеры могут читать и записывать в кеш")
            
            return True
        else:
            print("❌ Не удалось запустить ни одного контейнера")
            return False
    
    def stop_all_containers(self):
        """Остановка всех контейнеров"""
        print("🛑 Остановка существующих контейнеров...")
        
        # Получение списка всех контейнеров проекта
        container_names = []
        for model_config in self.models_config["vllm_models"].values():
            container_names.append(model_config["container_name"])
        
        for container_name in container_names:
            try:
                subprocess.run(["docker", "stop", container_name], 
                             check=False, capture_output=True)
                subprocess.run(["docker", "rm", container_name], 
                             check=False, capture_output=True)
            except:
                pass
        
        self.running_containers = []
    
    def wait_for_containers(self, timeout=300):
        """Ожидание готовности контейнеров"""
        if not self.running_containers:
            return False
        
        print("⏳ Ожидание готовности контейнеров...")
        
        ready_containers = []
        start_time = time.time()
        
        while len(ready_containers) < len(self.running_containers) and (time.time() - start_time) < timeout:
            for container in self.running_containers:
                if container["name"] in [c["name"] for c in ready_containers]:
                    continue
                
                try:
                    response = requests.get(f"http://localhost:{container['port']}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {container['config']['name']} готов")
                        ready_containers.append(container)
                except:
                    pass
            
            if len(ready_containers) < len(self.running_containers):
                time.sleep(10)
        
        if len(ready_containers) == len(self.running_containers):
            print("🎉 Все контейнеры готовы!")
            return True
        else:
            print(f"⚠️ Готово {len(ready_containers)} из {len(self.running_containers)} контейнеров")
            return False
    
    def show_status(self):
        """Показать текущий статус"""
        print("\n📊 ТЕКУЩИЙ СТАТУС")
        print("=" * 30)
        
        # GPU информация
        gpu_info = self.get_gpu_info()
        if gpu_info:
            print(f"🎮 GPU память: {gpu_info['used_gb']:.1f}/{gpu_info['total_gb']:.1f} GB")
            print(f"   Свободно: {gpu_info['free_gb']:.1f} GB")
        
        # Кеш информация
        print(f"📁 Кеш директория: {self.cache_dir}")
        if self.cache_dir.exists():
            cache_size = sum(f.stat().st_size for f in self.cache_dir.rglob('*') if f.is_file())
            print(f"💾 Размер кеша: {cache_size / (1024**3):.2f} GB")
        
        # Текущий режим
        print(f"🔧 Режим: {self.current_mode or 'Не запущен'}")
        
        # Запущенные контейнеры
        if self.running_containers:
            print(f"🐳 Контейнеры ({len(self.running_containers)}):")
            for container in self.running_containers:
                print(f"   • {container['config']['name']}: http://localhost:{container['port']}")
        else:
            print("🐳 Контейнеры: Не запущены")

def main():
    """Основная функция"""
    selector = ModelModeSelector()
    
    print("🎯 СЕЛЕКТОР РЕЖИМА РАБОТЫ МОДЕЛЕЙ")
    print("=" * 40)
    
    # Проверка кеша
    if not selector.check_cache_dir():
        print("❌ Проблемы с кеш директорией")
        return
    
    while True:
        print("\n🔧 ВЫБЕРИТЕ ДЕЙСТВИЕ:")
        print("1. 📊 Показать статус и рекомендации")
        print("2. 🤖 Запустить Transformers режим")
        print("3. 🚀 Запустить vLLM режим")
        print("4. 🛑 Остановить все контейнеры")
        print("5. ⏳ Проверить готовность контейнеров")
        print("6. 📁 Управление кешем")
        print("0. ❌ Выход")
        
        choice = input("\nВведите номер: ").strip()
        
        if choice == "1":
            selector.show_status()
            mode, reason = selector.recommend_mode()
            print(f"\n💡 Рекомендация: {mode.upper()} режим")
            print(f"   Причина: {reason}")
            
        elif choice == "2":
            print("\n🤖 TRANSFORMERS РЕЖИМ")
            print("Доступные модели:")
            for i, (model_name, config) in enumerate(selector.models_config["transformers_models"].items(), 1):
                print(f"{i}. {config['name']} ({config['size_gb']} GB, 8-bit: {config['memory_8bit_gb']} GB)")
            
            model_choice = input("Выберите модель (Enter для dots.ocr): ").strip()
            if model_choice.isdigit():
                model_names = list(selector.models_config["transformers_models"].keys())
                if 1 <= int(model_choice) <= len(model_names):
                    selected_model = model_names[int(model_choice) - 1]
                else:
                    selected_model = "rednote-hilab/dots.ocr"
            else:
                selected_model = "rednote-hilab/dots.ocr"
            
            selector.start_transformers_mode(selected_model)
            
        elif choice == "3":
            print("\n🚀 vLLM РЕЖИМ")
            print("Доступные модели:")
            for i, (model_name, config) in enumerate(selector.models_config["vllm_models"].items(), 1):
                print(f"{i}. {config['name']} ({config['size_gb']} GB, требует {config['memory_required_gb']} GB)")
            
            models_input = input("Выберите модели (через запятую, Enter для dots.ocr): ").strip()
            if models_input:
                model_indices = [int(x.strip()) for x in models_input.split(',') if x.strip().isdigit()]
                model_names = list(selector.models_config["vllm_models"].keys())
                selected_models = [model_names[i-1] for i in model_indices if 1 <= i <= len(model_names)]
            else:
                selected_models = ["rednote-hilab/dots.ocr"]
            
            if selector.start_vllm_mode(selected_models):
                selector.wait_for_containers()
            
        elif choice == "4":
            selector.stop_all_containers()
            selector.current_mode = None
            print("✅ Все контейнеры остановлены")
            
        elif choice == "5":
            if selector.running_containers:
                selector.wait_for_containers()
            else:
                print("❌ Нет запущенных контейнеров")
                
        elif choice == "6":
            print(f"\n📁 УПРАВЛЕНИЕ КЕШЕМ")
            print(f"Директория: {selector.cache_dir}")
            print("1. Показать содержимое кеша")
            print("2. Очистить кеш")
            
            cache_choice = input("Выберите действие: ").strip()
            if cache_choice == "1":
                if selector.cache_dir.exists():
                    for item in selector.cache_dir.iterdir():
                        if item.is_dir():
                            size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                            print(f"   📦 {item.name}: {size / (1024**3):.2f} GB")
                else:
                    print("📁 Кеш директория не существует")
            elif cache_choice == "2":
                confirm = input("⚠️ Удалить весь кеш? (yes/no): ").strip().lower()
                if confirm == "yes":
                    import shutil
                    if selector.cache_dir.exists():
                        shutil.rmtree(selector.cache_dir)
                        selector.cache_dir.mkdir(parents=True, exist_ok=True)
                        print("✅ Кеш очищен")
                    else:
                        print("📁 Кеш уже пуст")
                        
        elif choice == "0":
            selector.stop_all_containers()
            break
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()