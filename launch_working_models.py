#!/usr/bin/env python3
"""
Простой лаунчер для работающих vLLM моделей
"""

import json
import subprocess
import time
import requests
import os
from typing import Dict, Any

class WorkingModelsLauncher:
    def __init__(self):
        self.cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
        
        # Загрузка конфигурации работающих моделей
        try:
            with open('final_working_models.json', 'r', encoding='utf-8') as f:
                self.working_models = json.load(f)
        except FileNotFoundError:
            # Fallback конфигурация
            self.working_models = {
                "rednote-hilab/dots.ocr": {
                    "container_name": "dots-ocr-production",
                    "port": 8000,
                    "vllm_params": {
                        "max_model_len": 1024,
                        "gpu_memory_utilization": 0.85,
                        "trust_remote_code": True,
                        "enforce_eager": True
                    }
                },
                "Qwen/Qwen3-VL-2B-Instruct": {
                    "container_name": "qwen3-vl-2b-production",
                    "port": 8010,
                    "vllm_params": {
                        "max_model_len": 2048,
                        "gpu_memory_utilization": 0.7,
                        "trust_remote_code": True,
                        "enforce_eager": False
                    }
                }
            }
    
    def run_command(self, command):
        """Выполнение команды"""
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip() if e.stderr else str(e)
    
    def check_gpu_memory(self):
        """Проверка памяти GPU"""
        success, output = self.run_command("nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv,noheader,nounits")
        
        if success:
            lines = output.strip().split('\n')
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) == 3:
                    total, used, free = map(int, parts)
                    return {
                        'total_mb': total,
                        'used_mb': used,
                        'free_mb': free,
                        'usage_percent': round((used / total) * 100, 1)
                    }
        return None
    
    def cleanup_containers(self):
        """Очистка всех контейнеров vLLM"""
        print("🧹 Очистка старых контейнеров...")
        success, output = self.run_command("docker ps -a --filter ancestor=vllm/vllm-openai:latest --format {{.Names}}")
        
        if success and output:
            container_names = output.strip().split('\n')
            for container_name in container_names:
                if container_name:
                    self.run_command(f"docker stop {container_name}")
                    self.run_command(f"docker rm {container_name}")
                    print(f"   🗑️ Удален {container_name}")
    
    def launch_model(self, model_name: str, config: Dict[str, Any]) -> bool:
        """Запуск одной модели"""
        print(f"\n🚀 ЗАПУСК: {model_name}")
        print("-" * 50)
        
        container_name = config['container_name']
        port = config['port']
        vllm_params = config['vllm_params']
        
        # Проверка памяти
        gpu_info = self.check_gpu_memory()
        if gpu_info:
            print(f"💾 GPU: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
        
        # Формирование команды Docker
        docker_command = f"""
        docker run -d \
            --gpus all \
            --name {container_name} \
            -p {port}:{port} \
            -v {self.cache_path}:/root/.cache/huggingface/hub:ro \
            --shm-size=8g \
            vllm/vllm-openai:latest \
            --model {model_name} \
            --trust-remote-code \
            --max-model-len {vllm_params['max_model_len']} \
            --gpu-memory-utilization {vllm_params['gpu_memory_utilization']} \
            --host 0.0.0.0 \
            --port {port} \
            --disable-log-requests
        """.strip().replace('\n', ' ').replace('\\', '')
        
        if vllm_params.get('enforce_eager'):
            docker_command += " --enforce-eager"
        
        print(f"📦 Запуск контейнера {container_name} на порту {port}...")
        
        # Запуск контейнера
        success, output = self.run_command(docker_command)
        
        if not success:
            print(f"❌ Ошибка запуска: {output}")
            return False
        
        print(f"✅ Контейнер запущен: {output[:12]}...")
        
        # Ожидание готовности (с таймаутом)
        timeout = 300 if "dots.ocr" in model_name else 360  # 5-6 минут
        start_time = time.time()
        
        print(f"⏳ Ожидание готовности (таймаут {timeout}с)...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    launch_time = time.time() - start_time
                    print(f"✅ Модель готова за {int(launch_time)} секунд!")
                    
                    # Проверка памяти после запуска
                    gpu_info = self.check_gpu_memory()
                    if gpu_info:
                        print(f"💾 GPU после запуска: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
                    
                    return True
                    
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                print(f"⚠️ Ошибка проверки: {e}")
            
            # Показ прогресса каждые 30 секунд
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0 and elapsed > 0:
                print(f"   ⏳ {elapsed}/{timeout}с...")
            
            time.sleep(10)
        
        print(f"❌ Таймаут {timeout}с - модель не готова")
        return False
    
    def list_models(self):
        """Показ доступных моделей"""
        print("📋 ДОСТУПНЫЕ МОДЕЛИ:")
        print("=" * 30)
        
        for i, (model_name, config) in enumerate(self.working_models.items(), 1):
            port = config['port']
            container = config['container_name']
            print(f"{i}. {model_name}")
            print(f"   Порт: {port}")
            print(f"   Контейнер: {container}")
            print()
    
    def launch_single_model(self, model_choice: str):
        """Запуск одной выбранной модели"""
        model_names = list(self.working_models.keys())
        
        if model_choice.isdigit():
            choice = int(model_choice) - 1
            if 0 <= choice < len(model_names):
                model_name = model_names[choice]
            else:
                print(f"❌ Неверный выбор: {model_choice}")
                return False
        else:
            # Поиск по имени
            matching_models = [name for name in model_names if model_choice.lower() in name.lower()]
            if len(matching_models) == 1:
                model_name = matching_models[0]
            elif len(matching_models) > 1:
                print(f"❌ Найдено несколько моделей: {matching_models}")
                return False
            else:
                print(f"❌ Модель не найдена: {model_choice}")
                return False
        
        # Очистка контейнеров
        self.cleanup_containers()
        
        # Запуск модели
        config = self.working_models[model_name]
        success = self.launch_model(model_name, config)
        
        if success:
            port = config['port']
            print(f"\n🎉 МОДЕЛЬ ГОТОВА К РАБОТЕ!")
            print(f"🌐 API: http://localhost:{port}")
            print(f"📚 Документация: http://localhost:{port}/docs")
            print(f"❤️ Health: http://localhost:{port}/health")
            
            # Пример использования
            print(f"\n💡 ПРИМЕР ИСПОЛЬЗОВАНИЯ:")
            print(f"curl -X POST http://localhost:{port}/v1/chat/completions \\")
            print(f'  -H "Content-Type: application/json" \\')
            print(f'  -d \'{{"model": "{model_name}", "messages": [{{"role": "user", "content": "Hello!"}}]}}\'')
        
        return success
    
    def launch_all_models(self):
        """Запуск всех моделей"""
        print("🚀 ЗАПУСК ВСЕХ РАБОТАЮЩИХ МОДЕЛЕЙ")
        print("=" * 40)
        
        # Очистка контейнеров
        self.cleanup_containers()
        
        success_count = 0
        
        for model_name, config in self.working_models.items():
            success = self.launch_model(model_name, config)
            if success:
                success_count += 1
            
            # Пауза между запусками
            if model_name != list(self.working_models.keys())[-1]:
                print(f"\n⏸️ Пауза 10 секунд...")
                time.sleep(10)
        
        print(f"\n🏆 ИТОГ: {success_count}/{len(self.working_models)} моделей запущено")
        
        if success_count > 0:
            print(f"\n🌐 ДОСТУПНЫЕ API:")
            for model_name, config in self.working_models.items():
                port = config['port']
                print(f"• {model_name}: http://localhost:{port}")
        
        return success_count > 0
    
    def show_status(self):
        """Показ статуса запущенных контейнеров"""
        print("📊 СТАТУС КОНТЕЙНЕРОВ:")
        print("=" * 25)
        
        success, output = self.run_command("docker ps --filter ancestor=vllm/vllm-openai:latest --format 'table {{.Names}}\\t{{.Ports}}\\t{{.Status}}'")
        
        if success and output:
            print(output)
        else:
            print("Нет запущенных контейнеров vLLM")
        
        # Проверка GPU
        gpu_info = self.check_gpu_memory()
        if gpu_info:
            print(f"\n💾 GPU: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")

def main():
    """Основная функция"""
    launcher = WorkingModelsLauncher()
    
    print("🤖 ЛАУНЧЕР РАБОТАЮЩИХ vLLM МОДЕЛЕЙ")
    print("=" * 40)
    
    if len(launcher.working_models) == 0:
        print("❌ Нет доступных моделей для запуска")
        return
    
    while True:
        print(f"\n📋 МЕНЮ:")
        print("1. Показать доступные модели")
        print("2. Запустить одну модель")
        print("3. Запустить все модели")
        print("4. Показать статус")
        print("5. Очистить контейнеры")
        print("0. Выход")
        
        choice = input("\nВыберите действие: ").strip()
        
        if choice == "1":
            launcher.list_models()
        
        elif choice == "2":
            launcher.list_models()
            model_choice = input("Введите номер или название модели: ").strip()
            if model_choice:
                launcher.launch_single_model(model_choice)
        
        elif choice == "3":
            launcher.launch_all_models()
        
        elif choice == "4":
            launcher.show_status()
        
        elif choice == "5":
            launcher.cleanup_containers()
            print("✅ Контейнеры очищены")
        
        elif choice == "0":
            print("👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()