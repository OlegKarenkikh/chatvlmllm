#!/usr/bin/env python3
"""
Менеджер Docker Compose для vLLM моделей
Управление контейнерами с правильным монтированием кешей
"""

import subprocess
import time
import requests
import json
import os
from pathlib import Path

class VLLMDockerManager:
    def __init__(self):
        self.compose_file = "docker-compose-vllm.yml"
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        self.services = {
            "dots-ocr": {
                "name": "DotsOCR",
                "port": 8000,
                "model": "rednote-hilab/dots.ocr",
                "priority": 1
            },
            "qwen2-vl-2b": {
                "name": "Qwen2-VL 2B",
                "port": 8001,
                "model": "Qwen/Qwen2-VL-2B-Instruct",
                "priority": 2
            },
            "got-ocr": {
                "name": "GOT-OCR 2.0",
                "port": 8002,
                "model": "stepfun-ai/GOT-OCR-2.0-hf",
                "priority": 3
            }
        }
    
    def check_prerequisites(self):
        """Проверка предварительных условий"""
        print("🔍 Проверка предварительных условий...")
        
        # Проверка Docker
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker: {result.stdout.strip()}")
        except:
            print("❌ Docker не установлен или недоступен")
            return False
        
        # Проверка Docker Compose
        try:
            result = subprocess.run(["docker", "compose", "version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker Compose: {result.stdout.strip()}")
        except:
            print("❌ Docker Compose не установлен")
            return False
        
        # Проверка NVIDIA Docker
        try:
            result = subprocess.run(["docker", "run", "--rm", "--gpus", "all", 
                                   "nvidia/cuda:11.8-base-ubuntu20.04", "nvidia-smi"], 
                                  capture_output=True, text=True, check=True, timeout=30)
            print("✅ NVIDIA Docker runtime работает")
        except:
            print("⚠️ NVIDIA Docker runtime может быть недоступен")
        
        # Проверка кеш директории
        if not self.cache_dir.exists():
            print(f"📁 Создание кеш директории: {self.cache_dir}")
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Кеш директория: {self.cache_dir}")
        
        # Проверка compose файла
        if not Path(self.compose_file).exists():
            print(f"❌ Файл {self.compose_file} не найден")
            return False
        
        print(f"✅ Compose файл: {self.compose_file}")
        return True
    
    def run_compose_command(self, command, capture_output=True):
        """Выполнение команды docker compose"""
        cmd = ["docker", "compose", "-f", self.compose_file] + command
        print(f"🔄 {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=capture_output, 
                                  text=True, check=True)
            if capture_output and result.stdout:
                print(result.stdout)
            return True, result.stdout if capture_output else ""
        except subprocess.CalledProcessError as e:
            error_msg = f"Ошибка команды: {e}"
            if capture_output and e.stderr:
                error_msg += f"\nStderr: {e.stderr}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def start_service(self, service_name):
        """Запуск конкретного сервиса"""
        if service_name not in self.services:
            print(f"❌ Неизвестный сервис: {service_name}")
            return False
        
        service_info = self.services[service_name]
        print(f"🚀 Запуск {service_info['name']}...")
        
        success, output = self.run_compose_command(["up", "-d", service_name])
        if success:
            print(f"✅ {service_info['name']} запущен на порту {service_info['port']}")
            return True
        else:
            print(f"❌ Не удалось запустить {service_info['name']}")
            return False
    
    def stop_service(self, service_name):
        """Остановка конкретного сервиса"""
        if service_name not in self.services:
            print(f"❌ Неизвестный сервис: {service_name}")
            return False
        
        service_info = self.services[service_name]
        print(f"🛑 Остановка {service_info['name']}...")
        
        success, output = self.run_compose_command(["stop", service_name])
        if success:
            print(f"✅ {service_info['name']} остановлен")
            return True
        else:
            print(f"❌ Не удалось остановить {service_info['name']}")
            return False
    
    def start_all(self):
        """Запуск всех сервисов"""
        print("🚀 Запуск всех vLLM сервисов...")
        success, output = self.run_compose_command(["up", "-d"])
        return success
    
    def start_multi_model(self):
        """Запуск в многомодельном режиме"""
        print("🚀 Запуск в многомодельном режиме...")
        success, output = self.run_compose_command(["--profile", "multi-model", "up", "-d"])
        return success
    
    def stop_all(self):
        """Остановка всех сервисов"""
        print("🛑 Остановка всех сервисов...")
        success, output = self.run_compose_command(["down"])
        return success
    
    def restart_service(self, service_name):
        """Перезапуск сервиса"""
        print(f"🔄 Перезапуск {service_name}...")
        success, output = self.run_compose_command(["restart", service_name])
        return success
    
    def show_logs(self, service_name=None, follow=False):
        """Показать логи"""
        cmd = ["logs"]
        if follow:
            cmd.append("-f")
        if service_name:
            cmd.append(service_name)
        
        self.run_compose_command(cmd, capture_output=False)
    
    def show_status(self):
        """Показать статус сервисов"""
        print("\n📊 СТАТУС СЕРВИСОВ")
        print("=" * 50)
        
        # Статус контейнеров
        success, output = self.run_compose_command(["ps"])
        if success:
            print(output)
        
        # Проверка доступности API
        print("\n🌐 ПРОВЕРКА API:")
        for service_name, service_info in self.services.items():
            port = service_info['port']
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_info['name']}: http://localhost:{port} - Готов")
                else:
                    print(f"⚠️ {service_info['name']}: http://localhost:{port} - Ошибка {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"❌ {service_info['name']}: http://localhost:{port} - Недоступен")
            except Exception as e:
                print(f"⚠️ {service_info['name']}: http://localhost:{port} - {str(e)}")
    
    def wait_for_services(self, timeout=300):
        """Ожидание готовности сервисов"""
        print("⏳ Ожидание готовности сервисов...")
        
        start_time = time.time()
        ready_services = set()
        
        while len(ready_services) < len(self.services) and (time.time() - start_time) < timeout:
            for service_name, service_info in self.services.items():
                if service_name in ready_services:
                    continue
                
                try:
                    response = requests.get(f"http://localhost:{service_info['port']}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {service_info['name']} готов")
                        ready_services.add(service_name)
                except:
                    pass
            
            if len(ready_services) < len(self.services):
                time.sleep(10)
        
        if len(ready_services) == len(self.services):
            print("🎉 Все сервисы готовы!")
            return True
        else:
            print(f"⚠️ Готово {len(ready_services)} из {len(self.services)} сервисов")
            return False
    
    def check_cache_usage(self):
        """Проверка использования кеша"""
        print(f"\n📁 ИСПОЛЬЗОВАНИЕ КЕША")
        print("=" * 30)
        
        if not self.cache_dir.exists():
            print("❌ Кеш директория не существует")
            return
        
        # Размер кеша
        total_size = 0
        model_sizes = {}
        
        for item in self.cache_dir.iterdir():
            if item.is_dir() and item.name.startswith('models--'):
                model_name = item.name.replace('models--', '').replace('--', '/')
                size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                model_sizes[model_name] = size
                total_size += size
        
        print(f"📊 Общий размер кеша: {total_size / (1024**3):.2f} GB")
        
        if model_sizes:
            print("📦 Кешированные модели:")
            for model, size in sorted(model_sizes.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {model}: {size / (1024**3):.2f} GB")
        else:
            print("📦 Кеш пуст")

def main():
    """Основная функция"""
    manager = VLLMDockerManager()
    
    print("🐳 МЕНЕДЖЕР vLLM DOCKER КОНТЕЙНЕРОВ")
    print("=" * 45)
    
    if not manager.check_prerequisites():
        print("❌ Не все предварительные условия выполнены")
        return
    
    while True:
        print("\n🔧 ВЫБЕРИТЕ ДЕЙСТВИЕ:")
        print("1. 🚀 Запустить основной сервис (DotsOCR)")
        print("2. 🚀 Запустить все сервисы")
        print("3. 🚀 Запустить многомодельный режим")
        print("4. 🛑 Остановить все сервисы")
        print("5. 🔄 Перезапустить сервис")
        print("6. 📊 Показать статус")
        print("7. 📋 Показать логи")
        print("8. ⏳ Ждать готовности сервисов")
        print("9. 📁 Проверить кеш")
        print("0. ❌ Выход")
        
        choice = input("\nВведите номер: ").strip()
        
        if choice == "1":
            manager.start_service("dots-ocr")
            
        elif choice == "2":
            manager.start_all()
            
        elif choice == "3":
            manager.start_multi_model()
            
        elif choice == "4":
            manager.stop_all()
            
        elif choice == "5":
            print("\nДоступные сервисы:")
            for i, (service_name, service_info) in enumerate(manager.services.items(), 1):
                print(f"{i}. {service_info['name']} ({service_name})")
            
            service_choice = input("Выберите сервис: ").strip()
            if service_choice.isdigit():
                service_names = list(manager.services.keys())
                if 1 <= int(service_choice) <= len(service_names):
                    selected_service = service_names[int(service_choice) - 1]
                    manager.restart_service(selected_service)
                    
        elif choice == "6":
            manager.show_status()
            
        elif choice == "7":
            print("\nДоступные сервисы:")
            print("0. Все сервисы")
            for i, (service_name, service_info) in enumerate(manager.services.items(), 1):
                print(f"{i}. {service_info['name']} ({service_name})")
            
            service_choice = input("Выберите сервис (Enter для всех): ").strip()
            follow = input("Следить за логами? (y/n): ").strip().lower() == 'y'
            
            if service_choice == "0" or not service_choice:
                manager.show_logs(follow=follow)
            elif service_choice.isdigit():
                service_names = list(manager.services.keys())
                if 1 <= int(service_choice) <= len(service_names):
                    selected_service = service_names[int(service_choice) - 1]
                    manager.show_logs(selected_service, follow=follow)
                    
        elif choice == "8":
            manager.wait_for_services()
            
        elif choice == "9":
            manager.check_cache_usage()
            
        elif choice == "0":
            break
            
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()