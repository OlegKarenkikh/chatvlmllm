#!/usr/bin/env python3
"""
Многомодельный лаунчер для vLLM с управлением ресурсами
"""

import json
import subprocess
import time
import requests
import os
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any

class MultiModelLauncher:
    def __init__(self, config_file: str = "vllm_models_config.json"):
        self.config_file = config_file
        self.configs = self.load_configs()
        self.cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
        self.running_containers = {}
        
    def load_configs(self) -> Dict[str, Any]:
        """Загрузка конфигураций моделей"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Файл конфигурации {self.config_file} не найден")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка в JSON файле: {e}")
            return {}
    
    def run_command(self, command: str, capture_output: bool = True) -> tuple[bool, str]:
        """Выполнение команды"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=capture_output, 
                text=True
            )
            return True, result.stdout.strip() if result.stdout else ""
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            return False, error_msg
    
    def check_gpu_memory(self) -> Dict[str, Any]:
        """Проверка доступной памяти GPU"""
        success, output = self.run_command("nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv,noheader,nounits")
        
        if success:
            lines = output.strip().split('\n')
            gpu_info = []
            
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) == 3:
                    total, used, free = map(int, parts)
                    gpu_info.append({
                        'gpu_id': i,
                        'total_mb': total,
                        'used_mb': used,
                        'free_mb': free,
                        'usage_percent': round((used / total) * 100, 1)
                    })
            
            return {'success': True, 'gpus': gpu_info}
        else:
            return {'success': False, 'error': output}
    
    def get_running_containers(self) -> List[Dict[str, str]]:
        """Получение списка запущенных контейнеров vLLM"""
        success, output = self.run_command("docker ps --filter ancestor=vllm/vllm-openai:latest --format json")
        
        containers = []
        if success and output:
            for line in output.strip().split('\n'):
                try:
                    container_info = json.loads(line)
                    containers.append({
                        'id': container_info['ID'],
                        'name': container_info['Names'],
                        'ports': container_info['Ports'],
                        'status': container_info['Status']
                    })
                except json.JSONDecodeError:
                    continue
        
        return containers
    
    def stop_container(self, container_name: str) -> bool:
        """Остановка контейнера"""
        print(f"🛑 Остановка контейнера {container_name}...")
        
        success, _ = self.run_command(f"docker stop {container_name}")
        if success:
            self.run_command(f"docker rm {container_name}")
            return True
        return False
    
    def wait_for_model(self, port: int, model_name: str, timeout: int = 300) -> bool:
        """Ожидание готовности модели"""
        print(f"⏳ Ожидание готовности {model_name} на порту {port}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {model_name} готова!")
                    return True
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                print(f"⚠️ Ошибка проверки {model_name}: {e}")
            
            time.sleep(10)
        
        print(f"❌ {model_name} не запустилась за {timeout} секунд")
        return False
    
    def launch_model(self, model_name: str, wait: bool = True) -> bool:
        """Запуск одной модели"""
        if model_name not in self.configs:
            print(f"❌ Модель {model_name} не найдена в конфигурации")
            return False
        
        config = self.configs[model_name]
        container_name = config['container_name']
        port = config['port']
        
        # Остановка существующего контейнера
        self.stop_container(container_name)
        
        # Формирование команды Docker
        vllm_params = config['vllm_params']
        
        docker_command = f"""
        docker run -d \
            --gpus all \
            --name {container_name} \
            --restart unless-stopped \
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
        
        # Добавление дополнительных параметров
        if vllm_params.get('enforce_eager'):
            docker_command += " --enforce-eager"
        
        print(f"🚀 Запуск {model_name} на порту {port}...")
        print(f"📦 Контейнер: {container_name}")
        print(f"💾 Размер модели: {config['size_gb']} ГБ")
        
        success, output = self.run_command(docker_command)
        
        if success:
            print(f"✅ Контейнер {container_name} запущен")
            
            if wait:
                if self.wait_for_model(port, model_name):
                    self.running_containers[model_name] = {
                        'container_name': container_name,
                        'port': port,
                        'status': 'running'
                    }
                    return True
                else:
                    print(f"❌ Модель {model_name} не готова")
                    return False
            else:
                self.running_containers[model_name] = {
                    'container_name': container_name,
                    'port': port,
                    'status': 'starting'
                }
                return True
        else:
            print(f"❌ Ошибка запуска {model_name}: {output}")
            return False
    
    def launch_multiple_models(self, model_names: List[str], sequential: bool = True) -> Dict[str, bool]:
        """Запуск нескольких моделей"""
        results = {}
        
        if sequential:
            print("🔄 Последовательный запуск моделей...")
            for model_name in model_names:
                results[model_name] = self.launch_model(model_name, wait=True)
                if not results[model_name]:
                    print(f"⚠️ Остановка запуска из-за ошибки с {model_name}")
                    break
        else:
            print("🔄 Параллельный запуск моделей...")
            # Запуск всех без ожидания
            for model_name in model_names:
                results[model_name] = self.launch_model(model_name, wait=False)
            
            # Ожидание готовности всех
            for model_name in model_names:
                if results[model_name]:
                    config = self.configs[model_name]
                    port = config['port']
                    if self.wait_for_model(port, model_name):
                        self.running_containers[model_name]['status'] = 'running'
                    else:
                        results[model_name] = False
        
        return results
    
    def stop_all_models(self):
        """Остановка всех моделей"""
        print("🛑 Остановка всех моделей...")
        
        containers = self.get_running_containers()
        for container in containers:
            self.stop_container(container['name'])
        
        self.running_containers.clear()
        print("✅ Все модели остановлены")
    
    def show_status(self):
        """Показать статус всех моделей"""
        print("📊 СТАТУС МОДЕЛЕЙ")
        print("=" * 40)
        
        # Проверка GPU
        gpu_info = self.check_gpu_memory()
        if gpu_info['success']:
            for gpu in gpu_info['gpus']:
                print(f"🎮 GPU {gpu['gpu_id']}: {gpu['used_mb']}/{gpu['total_mb']} МБ ({gpu['usage_percent']}%)")
        
        print()
        
        # Запущенные контейнеры
        containers = self.get_running_containers()
        if containers:
            print("🟢 ЗАПУЩЕННЫЕ МОДЕЛИ:")
            for container in containers:
                print(f"   • {container['name']} - {container['status']}")
                print(f"     Порты: {container['ports']}")
        else:
            print("🔴 Нет запущенных моделей")
        
        print()
        
        # Доступные модели
        print("📋 ДОСТУПНЫЕ МОДЕЛИ:")
        sorted_models = sorted(self.configs.items(), key=lambda x: x[1]['priority'])
        
        for model_name, config in sorted_models:
            status = "🟢" if any(c['name'] == config['container_name'] for c in containers) else "🔴"
            print(f"   {status} {model_name}")
            print(f"      Категория: {config['category']}")
            print(f"      Размер: {config['size_gb']} ГБ")
            print(f"      Порт: {config['port']}")
            if config['issues']:
                print(f"      Проблемы: {', '.join(config['issues'])}")
    
    def create_unified_client(self):
        """Создание унифицированного клиента для всех моделей"""
        client_code = '''#!/usr/bin/env python3
"""
Унифицированный клиент для всех моделей vLLM
"""

import requests
import base64
import json
from pathlib import Path
from typing import Dict, Any, Optional

class UnifiedVLLMClient:
    def __init__(self):
        self.models = {}
        self.load_model_configs()
    
    def load_model_configs(self):
        """Загрузка конфигураций моделей"""
        try:
            with open('vllm_models_config.json', 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            for model_name, config in configs.items():
                self.models[model_name] = {
                    'url': f"http://localhost:{config['port']}",
                    'category': config['category'],
                    'port': config['port']
                }
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигураций: {e}")
    
    def check_model_health(self, model_name: str) -> bool:
        """Проверка доступности модели"""
        if model_name not in self.models:
            return False
        
        try:
            url = self.models[model_name]['url']
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Получение списка доступных моделей"""
        available = {}
        for model_name, config in self.models.items():
            if self.check_model_health(model_name):
                available[model_name] = config
        return available
    
    def process_image(self, model_name: str, image_path: str, 
                     prompt: str = "Extract all text from this image") -> Dict[str, Any]:
        """Обработка изображения"""
        if not self.check_model_health(model_name):
            return {"success": False, "error": f"Модель {model_name} недоступна"}
        
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            ext = Path(image_path).suffix.lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg', 
                '.jpeg': 'image/jpeg'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            payload = {
                "model": model_name,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}}
                    ]
                }],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            url = self.models[model_name]['url']
            response = requests.post(f"{url}/v1/chat/completions", json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "text": result["choices"][0]["message"]["content"],
                    "model": model_name,
                    "usage": result.get("usage", {})
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    client = UnifiedVLLMClient()
    
    print("🚀 УНИФИЦИРОВАННЫЙ КЛИЕНТ VLLM")
    print("=" * 35)
    
    available = client.get_available_models()
    if available:
        print("✅ Доступные модели:")
        for model_name, config in available.items():
            print(f"   • {model_name} (порт {config['port']}, {config['category']})")
    else:
        print("❌ Нет доступных моделей")

if __name__ == "__main__":
    main()
'''
        
        with open('unified_vllm_client.py', 'w', encoding='utf-8') as f:
            f.write(client_code)
        
        print("💾 Унифицированный клиент создан: unified_vllm_client.py")

def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(description="Многомодельный лаунчер vLLM")
    parser.add_argument("--launch", nargs="+", help="Запустить модели")
    parser.add_argument("--launch-all", action="store_true", help="Запустить все модели")
    parser.add_argument("--launch-ocr", action="store_true", help="Запустить только OCR модели")
    parser.add_argument("--launch-vlm", action="store_true", help="Запустить только VLM модели")
    parser.add_argument("--stop-all", action="store_true", help="Остановить все модели")
    parser.add_argument("--status", action="store_true", help="Показать статус")
    parser.add_argument("--sequential", action="store_true", help="Последовательный запуск")
    parser.add_argument("--create-client", action="store_true", help="Создать унифицированный клиент")
    
    args = parser.parse_args()
    
    launcher = MultiModelLauncher()
    
    if not launcher.configs:
        print("❌ Нет доступных конфигураций моделей")
        return
    
    if args.status:
        launcher.show_status()
        return
    
    if args.stop_all:
        launcher.stop_all_models()
        return
    
    if args.create_client:
        launcher.create_unified_client()
        return
    
    # Определение моделей для запуска
    models_to_launch = []
    
    if args.launch:
        models_to_launch = args.launch
    elif args.launch_all:
        models_to_launch = list(launcher.configs.keys())
    elif args.launch_ocr:
        models_to_launch = [name for name, config in launcher.configs.items() 
                           if config['category'] == 'ocr']
    elif args.launch_vlm:
        models_to_launch = [name for name, config in launcher.configs.items() 
                           if config['category'] == 'vlm']
    
    if models_to_launch:
        print(f"🚀 ЗАПУСК МОДЕЛЕЙ: {len(models_to_launch)}")
        print("=" * 40)
        
        # Проверка GPU памяти
        gpu_info = launcher.check_gpu_memory()
        if gpu_info['success']:
            total_memory = sum(gpu['free_mb'] for gpu in gpu_info['gpus'])
            print(f"💾 Доступная GPU память: {total_memory} МБ")
        
        # Запуск моделей
        results = launcher.launch_multiple_models(models_to_launch, args.sequential)
        
        # Отчет о результатах
        print("\n📊 РЕЗУЛЬТАТЫ ЗАПУСКА:")
        print("=" * 25)
        
        successful = [name for name, success in results.items() if success]
        failed = [name for name, success in results.items() if not success]
        
        if successful:
            print("✅ Успешно запущены:")
            for model_name in successful:
                config = launcher.configs[model_name]
                print(f"   • {model_name} (порт {config['port']})")
        
        if failed:
            print("❌ Не удалось запустить:")
            for model_name in failed:
                print(f"   • {model_name}")
        
        print(f"\n🎯 Итого: {len(successful)}/{len(models_to_launch)} моделей запущено")
        
        if successful:
            print("\n💡 Создайте унифицированный клиент:")
            print("   python multi_model_launcher.py --create-client")
    else:
        launcher.show_status()
        print("\n💡 Примеры использования:")
        print("   python multi_model_launcher.py --launch-ocr")
        print("   python multi_model_launcher.py --launch rednote-hilab/dots.ocr")
        print("   python multi_model_launcher.py --launch-all --sequential")
        print("   python multi_model_launcher.py --status")
        print("   python multi_model_launcher.py --stop-all")

if __name__ == "__main__":
    main()