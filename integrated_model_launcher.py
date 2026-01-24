#!/usr/bin/env python3
"""
Интегрированный запускатель моделей
Объединяет Transformers и vLLM режимы с правильным управлением кешами
"""

import subprocess
import time
import requests
import json
import os
import threading
from pathlib import Path

class IntegratedModelLauncher:
    def __init__(self):
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        self.current_mode = None
        self.running_processes = []
        self.running_containers = []
        
        # Конфигурация моделей (проверенная совместимость)
        self.models_config = {
            "transformers": {
                "rednote-hilab/dots.ocr": {
                    "name": "DotsOCR",
                    "memory_8bit_gb": 3.5,
                    "port": 8000,
                    "category": "ocr",
                    "tested": True
                },
                "stepfun-ai/GOT-OCR-2.0-hf": {
                    "name": "GOT-OCR 2.0", 
                    "memory_8bit_gb": 0.8,
                    "port": 8001,
                    "category": "ocr",
                    "tested": False,
                    "issues": ["Requires specific prompt format"]
                },
                "Qwen/Qwen2-VL-2B-Instruct": {
                    "name": "Qwen2-VL 2B",
                    "memory_8bit_gb": 2.5,
                    "port": 8002,
                    "category": "vlm",
                    "tested": False
                },
                "microsoft/Phi-3.5-vision-instruct": {
                    "name": "Phi-3.5 Vision",
                    "memory_8bit_gb": 4.5,
                    "port": 8003,
                    "category": "vlm",
                    "tested": False
                },
                "vikhyatk/moondream2": {
                    "name": "Moondream2",
                    "memory_8bit_gb": 2.0,
                    "port": 8004,
                    "category": "vlm",
                    "tested": False,
                    "issues": ["Custom architecture - may need special handling"]
                }
            },
            "vllm": {
                "rednote-hilab/dots.ocr": {
                    "name": "DotsOCR",
                    "container_name": "rednote-hilab-dots-ocr-vllm",
                    "memory_required_gb": 8.0,
                    "port": 8000,
                    "category": "ocr",
                    "tested": True
                },
                "Qwen/Qwen2-VL-2B-Instruct": {
                    "name": "Qwen2-VL 2B",
                    "container_name": "qwen-qwen2-vl-2b-instruct-vllm", 
                    "memory_required_gb": 6.0,
                    "port": 8001,
                    "category": "vlm",
                    "tested": False
                },
                "microsoft/Phi-3.5-vision-instruct": {
                    "name": "Phi-3.5 Vision",
                    "container_name": "microsoft-phi-3-5-vision-instruct-vllm",
                    "memory_required_gb": 10.0,
                    "port": 8002,
                    "category": "vlm",
                    "tested": False,
                    "issues": ["May require specific vLLM version"]
                },
                "Qwen/Qwen2-VL-7B-Instruct": {
                    "name": "Qwen2-VL 7B",
                    "container_name": "qwen-qwen2-vl-7b-instruct-vllm",
                    "memory_required_gb": 12.0,
                    "port": 8003,
                    "category": "vlm",
                    "tested": False,
                    "issues": ["Requires high-end GPU"]
                }
            }
        }
    
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
        except Exception:
            return None
    
    def check_cache_setup(self):
        """Проверка и настройка кеша"""
        print(f"📁 Проверка кеш директории: {self.cache_dir}")
        
        if not self.cache_dir.exists():
            print("📁 Создание кеш директории...")
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Проверка прав доступа
        if not os.access(self.cache_dir, os.R_OK | os.W_OK):
            print("⚠️ Недостаточно прав для кеш директории")
            try:
                os.chmod(self.cache_dir, 0o755)
                print("✅ Права доступа исправлены")
            except:
                print("❌ Не удалось исправить права доступа")
                return False
        
        # Проверка существующих моделей
        cached_models = []
        total_cache_size = 0
        
        for item in self.cache_dir.iterdir():
            if item.is_dir() and item.name.startswith('models--'):
                model_name = item.name.replace('models--', '').replace('--', '/')
                size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                cached_models.append((model_name, size))
                total_cache_size += size
        
        if cached_models:
            print(f"✅ Найдено {len(cached_models)} кешированных моделей:")
            print(f"💾 Общий размер кеша: {total_cache_size / (1024**3):.2f} GB")
            for model_name, size in sorted(cached_models, key=lambda x: x[1], reverse=True):
                print(f"   • {model_name}: {size / (1024**3):.2f} GB")
        else:
            print("📥 Кеш пуст, модели будут загружены при первом использовании")
        
        return True
    
    def recommend_mode(self):
        """Рекомендация режима на основе доступных ресурсов"""
        gpu_info = self.get_gpu_info()
        
        if not gpu_info:
            return "transformers", "GPU недоступна, рекомендуется Transformers (CPU)"
        
        free_gb = gpu_info['free_gb']
        total_gb = gpu_info['total_gb']
        
        print(f"📊 GPU память: {free_gb:.1f} GB свободно из {total_gb:.1f} GB")
        
        if free_gb >= 10:
            return "vllm", f"Отличная производительность с vLLM ({free_gb:.1f} GB свободно)"
        elif free_gb >= 6:
            return "vllm", f"Хорошая производительность с vLLM ({free_gb:.1f} GB свободно)"
        elif free_gb >= 3:
            return "transformers", f"Рекомендуется Transformers режим ({free_gb:.1f} GB свободно)"
        else:
            return "transformers", f"Только Transformers режим возможен ({free_gb:.1f} GB свободно)"
    
    def start_transformers_mode(self, models=None):
        """Запуск Transformers режима"""
        if not models:
            models = ["rednote-hilab/dots.ocr"]
        
        print(f"🤖 Запуск Transformers режима с моделями: {', '.join(models)}")
        
        # Остановка существующих процессов
        self.stop_all()
        
        # Запуск многомодельного сервера
        cmd = [
            "python", "transformers_multi_model_server.py"
        ]
        
        try:
            print("🔄 Запуск многомодельного Transformers сервера...")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running_processes.append({
                "process": process,
                "name": "Transformers Multi-Model Server",
                "port": 8000,
                "models": models
            })
            
            self.current_mode = "transformers"
            
            # Ожидание запуска сервера
            print("⏳ Ожидание запуска сервера...")
            time.sleep(10)
            
            # Автозагрузка моделей
            for model in models:
                if model in self.models_config["transformers"]:
                    print(f"🔄 Загрузка модели {model}...")
                    self.load_transformers_model(model)
            
            print("✅ Transformers режим запущен")
            print("📡 API доступно на: http://localhost:8000")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска Transformers режима: {e}")
            return False
    
    def load_transformers_model(self, model_name):
        """Загрузка модели в Transformers режиме"""
        try:
            payload = {"model": model_name}
            response = requests.post("http://localhost:8000/models/load", 
                                   json=payload, timeout=300)
            if response.status_code == 200:
                print(f"✅ Модель {model_name} загружена")
                return True
            else:
                print(f"❌ Ошибка загрузки {model_name}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Ошибка загрузки {model_name}: {e}")
            return False
    
    def start_vllm_mode(self, models=None):
        """Запуск vLLM режима через Docker Compose"""
        if not models:
            models = ["rednote-hilab/dots.ocr"]
        
        print(f"🚀 Запуск vLLM режима с моделями: {', '.join(models)}")
        
        # Остановка существующих контейнеров
        self.stop_all()
        
        # Подготовка переменных окружения
        env = os.environ.copy()
        env["HOME"] = str(Path.home())
        
        # Запуск через Docker Compose
        try:
            if len(models) == 1 and models[0] == "rednote-hilab/dots.ocr":
                # Запуск только основной модели
                cmd = ["docker", "compose", "-f", "docker-compose-vllm.yml", "up", "-d", "dots-ocr"]
            else:
                # Многомодельный режим
                cmd = ["docker", "compose", "-f", "docker-compose-vllm.yml", 
                       "--profile", "multi-model", "up", "-d"]
            
            print(f"🔄 Выполнение: {' '.join(cmd)}")
            result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
            
            self.current_mode = "vllm"
            
            # Получение информации о запущенных контейнерах
            self.running_containers = []
            for model in models:
                if model in self.models_config["vllm"]:
                    config = self.models_config["vllm"][model]
                    self.running_containers.append({
                        "name": config["container_name"],
                        "model": model,
                        "port": config["port"],
                        "config": config
                    })
            
            print("✅ vLLM контейнеры запущены")
            print(f"📁 Кеш примонтирован: {self.cache_dir}")
            
            for container in self.running_containers:
                print(f"📡 {container['config']['name']}: http://localhost:{container['port']}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка запуска vLLM: {e}")
            if e.stderr:
                print(f"❌ Stderr: {e.stderr}")
            return False
    
    def stop_all(self):
        """Остановка всех процессов и контейнеров"""
        print("🛑 Остановка всех сервисов...")
        
        # Остановка Python процессов
        for proc_info in self.running_processes:
            try:
                proc_info["process"].terminate()
                proc_info["process"].wait(timeout=10)
                print(f"✅ Остановлен {proc_info['name']}")
            except:
                try:
                    proc_info["process"].kill()
                except:
                    pass
        
        self.running_processes = []
        
        # Остановка Docker контейнеров
        try:
            subprocess.run(["docker", "compose", "-f", "docker-compose-vllm.yml", "down"], 
                         check=False, capture_output=True)
            print("✅ Docker контейнеры остановлены")
        except:
            pass
        
        self.running_containers = []
        self.current_mode = None
    
    def wait_for_services(self, timeout=300):
        """Ожидание готовности сервисов"""
        print("⏳ Ожидание готовности сервисов...")
        
        if self.current_mode == "transformers":
            endpoints = [{"name": "Transformers Server", "port": 8000}]
        elif self.current_mode == "vllm":
            endpoints = [{"name": container["config"]["name"], "port": container["port"]} 
                        for container in self.running_containers]
        else:
            print("❌ Нет запущенных сервисов")
            return False
        
        start_time = time.time()
        ready_services = set()
        
        while len(ready_services) < len(endpoints) and (time.time() - start_time) < timeout:
            for endpoint in endpoints:
                if endpoint["name"] in ready_services:
                    continue
                
                try:
                    response = requests.get(f"http://localhost:{endpoint['port']}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {endpoint['name']} готов")
                        ready_services.add(endpoint["name"])
                except:
                    pass
            
            if len(ready_services) < len(endpoints):
                time.sleep(10)
        
        if len(ready_services) == len(endpoints):
            print("🎉 Все сервисы готовы!")
            return True
        else:
            print(f"⚠️ Готово {len(ready_services)} из {len(endpoints)} сервисов")
            return False
    
    def show_status(self):
        """Показать текущий статус"""
        print("\n📊 ТЕКУЩИЙ СТАТУС СИСТЕМЫ")
        print("=" * 40)
        
        # GPU информация
        gpu_info = self.get_gpu_info()
        if gpu_info:
            print(f"🎮 GPU память: {gpu_info['used_gb']:.1f}/{gpu_info['total_gb']:.1f} GB")
            print(f"   Свободно: {gpu_info['free_gb']:.1f} GB")
        else:
            print("🎮 GPU: Недоступна")
        
        # Кеш информация
        print(f"📁 Кеш: {self.cache_dir}")
        if self.cache_dir.exists():
            cache_size = sum(f.stat().st_size for f in self.cache_dir.rglob('*') if f.is_file())
            print(f"💾 Размер кеша: {cache_size / (1024**3):.2f} GB")
        
        # Текущий режим
        print(f"🔧 Режим: {self.current_mode or 'Не запущен'}")
        
        # Запущенные сервисы
        if self.current_mode == "transformers" and self.running_processes:
            print("🤖 Transformers сервер: http://localhost:8000")
        elif self.current_mode == "vllm" and self.running_containers:
            print(f"🚀 vLLM контейнеры ({len(self.running_containers)}):")
            for container in self.running_containers:
                print(f"   • {container['config']['name']}: http://localhost:{container['port']}")
        else:
            print("📡 Сервисы: Не запущены")
        
        # Рекомендация
        mode, reason = self.recommend_mode()
        print(f"\n💡 Рекомендация: {mode.upper()} режим")
        print(f"   Причина: {reason}")

def main():
    """Основная функция"""
    launcher = IntegratedModelLauncher()
    
    print("🎯 ИНТЕГРИРОВАННЫЙ ЗАПУСКАТЕЛЬ МОДЕЛЕЙ")
    print("=" * 50)
    
    # Проверка кеша
    if not launcher.check_cache_setup():
        print("❌ Проблемы с настройкой кеша")
        return
    
    while True:
        print("\n🔧 ВЫБЕРИТЕ РЕЖИМ РАБОТЫ:")
        print("1. 📊 Показать статус и рекомендации")
        print("2. 🤖 Запустить Transformers режим")
        print("3. 🚀 Запустить vLLM режим")
        print("4. 🔄 Переключить режим")
        print("5. 🛑 Остановить все сервисы")
        print("6. ⏳ Проверить готовность сервисов")
        print("7. 🧪 Тестировать текущий режим")
        print("8. 📁 Управление кешем")
        print("0. ❌ Выход")
        
        choice = input("\nВведите номер: ").strip()
        
        if choice == "1":
            launcher.show_status()
            
        elif choice == "2":
            print("\n🤖 TRANSFORMERS РЕЖИМ")
            print("Выберите модели для загрузки:")
            models = list(launcher.models_config["transformers"].keys())
            for i, model in enumerate(models, 1):
                config = launcher.models_config["transformers"][model]
                print(f"{i}. {config['name']} ({config['memory_8bit_gb']} GB)")
            
            selection = input("Выберите модели (через запятую, Enter для DotsOCR): ").strip()
            if selection:
                indices = [int(x.strip()) for x in selection.split(',') if x.strip().isdigit()]
                selected_models = [models[i-1] for i in indices if 1 <= i <= len(models)]
            else:
                selected_models = ["rednote-hilab/dots.ocr"]
            
            if launcher.start_transformers_mode(selected_models):
                launcher.wait_for_services()
            
        elif choice == "3":
            print("\n🚀 vLLM РЕЖИМ")
            print("Выберите модели для запуска:")
            models = list(launcher.models_config["vllm"].keys())
            for i, model in enumerate(models, 1):
                config = launcher.models_config["vllm"][model]
                print(f"{i}. {config['name']} ({config['memory_required_gb']} GB)")
            
            selection = input("Выберите модели (через запятую, Enter для DotsOCR): ").strip()
            if selection:
                indices = [int(x.strip()) for x in selection.split(',') if x.strip().isdigit()]
                selected_models = [models[i-1] for i in indices if 1 <= i <= len(models)]
            else:
                selected_models = ["rednote-hilab/dots.ocr"]
            
            if launcher.start_vllm_mode(selected_models):
                launcher.wait_for_services()
            
        elif choice == "4":
            if launcher.current_mode == "transformers":
                print("🔄 Переключение с Transformers на vLLM...")
                launcher.start_vllm_mode()
                launcher.wait_for_services()
            elif launcher.current_mode == "vllm":
                print("🔄 Переключение с vLLM на Transformers...")
                launcher.start_transformers_mode()
                launcher.wait_for_services()
            else:
                print("❌ Нет активного режима для переключения")
                
        elif choice == "5":
            launcher.stop_all()
            print("✅ Все сервисы остановлены")
            
        elif choice == "6":
            launcher.wait_for_services()
            
        elif choice == "7":
            if launcher.current_mode:
                print(f"🧪 Тестирование {launcher.current_mode} режима...")
                subprocess.run(["python", "test_memory_optimized_ocr.py"])
            else:
                print("❌ Нет активного режима для тестирования")
                
        elif choice == "8":
            print(f"\n📁 УПРАВЛЕНИЕ КЕШЕМ")
            print(f"Директория: {launcher.cache_dir}")
            print("1. Показать содержимое")
            print("2. Очистить кеш")
            print("3. Проверить целостность")
            
            cache_choice = input("Выберите действие: ").strip()
            if cache_choice == "1":
                launcher.check_cache_setup()
            elif cache_choice == "2":
                confirm = input("⚠️ Удалить весь кеш? (yes/no): ").strip().lower()
                if confirm == "yes":
                    import shutil
                    if launcher.cache_dir.exists():
                        shutil.rmtree(launcher.cache_dir)
                        launcher.cache_dir.mkdir(parents=True, exist_ok=True)
                        print("✅ Кеш очищен")
            elif cache_choice == "3":
                launcher.check_cache_setup()
                
        elif choice == "0":
            launcher.stop_all()
            break
            
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()