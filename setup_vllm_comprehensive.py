#!/usr/bin/env python3
"""
Комплексная настройка vLLM с поддержкой всех кешированных моделей
Приоритет: dots.ocr и другие OCR модели
"""

import subprocess
import time
import requests
import sys
import os
import json
import yaml
from pathlib import Path

class VLLMSetup:
    def __init__(self):
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        self.models_config = {}
        self.running_containers = []
        
    def run_command(self, command, shell=True, check=True):
        """Выполнение команды с логированием"""
        print(f"🔄 Выполняем: {command}")
        try:
            result = subprocess.run(command, shell=shell, check=check, 
                                  capture_output=True, text=True)
            if result.stdout:
                print(f"✅ {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка: {e}")
            if e.stderr:
                print(f"❌ Stderr: {e.stderr}")
            return None

    def check_prerequisites(self):
        """Проверка предварительных требований"""
        print("🔍 ПРОВЕРКА ПРЕДВАРИТЕЛЬНЫХ ТРЕБОВАНИЙ")
        print("=" * 50)
        
        # Проверка Docker
        result = self.run_command("docker --version", check=False)
        if result is None:
            print("❌ Docker не установлен")
            return False
        
        # Проверка NVIDIA драйвера
        result = self.run_command("nvidia-smi", check=False)
        if result is None:
            print("❌ NVIDIA драйвер недоступен")
            return False
        
        # Проверка GPU в Docker
        result = self.run_command("docker run --rm --gpus all nvidia/cuda:12.8-base-ubuntu22.04 nvidia-smi", check=False)
        if result is None:
            print("❌ GPU недоступен в Docker")
            return False
        
        print("✅ Все предварительные требования выполнены")
        return True

    def analyze_cached_models(self):
        """Анализ кешированных моделей"""
        print("\n🔍 АНАЛИЗ КЕШИРОВАННЫХ МОДЕЛЕЙ")
        print("=" * 40)
        
        if not self.cache_dir.exists():
            print("❌ Директория кеша HuggingFace не найдена!")
            return {}
        
        model_dirs = [d for d in self.cache_dir.iterdir() if d.is_dir() and d.name.startswith('models--')]
        
        models = {
            'ocr': [],
            'vlm': [],
            'other': []
        }
        
        for model_dir in model_dirs:
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            
            # Проверка наличия файлов модели
            snapshots_dir = model_dir / "snapshots"
            if not snapshots_dir.exists():
                continue
                
            snapshot_dirs = [d for d in snapshots_dir.iterdir() if d.is_dir()]
            if not snapshot_dirs:
                continue
            
            # Определение типа модели
            if any(keyword in model_name.lower() for keyword in ['ocr', 'got', 'dots']):
                models['ocr'].append(model_name)
            elif any(keyword in model_name.lower() for keyword in ['vision', 'vlm', 'qwen', 'phi']):
                models['vlm'].append(model_name)
            else:
                models['other'].append(model_name)
        
        print(f"📊 Найдено моделей:")
        print(f"   OCR: {len(models['ocr'])}")
        print(f"   VLM: {len(models['vlm'])}")
        print(f"   Другие: {len(models['other'])}")
        
        return models

    def create_vllm_config(self, models):
        """Создание конфигурации для vLLM"""
        print("\n📝 СОЗДАНИЕ КОНФИГУРАЦИИ VLLM")
        print("=" * 35)
        
        # Приоритетные модели для запуска
        priority_models = {
            'dots_ocr': 'rednote-hilab/dots.ocr',
            'got_ocr': 'stepfun-ai/GOT-OCR2_0',
            'deepseek_ocr': 'deepseek-ai/deepseek-ocr',
            'qwen3_vl': 'Qwen/Qwen3-VL-2B-Instruct',
            'phi3_vision': 'microsoft/Phi-3.5-vision-instruct'
        }
        
        # Проверка доступности приоритетных моделей
        available_models = {}
        all_models = models['ocr'] + models['vlm'] + models['other']
        
        for key, model_name in priority_models.items():
            if model_name in all_models:
                available_models[key] = model_name
                print(f"✅ {key}: {model_name}")
            else:
                print(f"❌ {key}: {model_name} (не найдена)")
        
        self.models_config = available_models
        return available_models

    def start_dots_ocr_container(self):
        """Запуск контейнера dots.ocr (приоритет)"""
        if 'dots_ocr' not in self.models_config:
            print("❌ dots.ocr не найдена в кеше")
            return False
            
        print("\n🚀 ЗАПУСК DOTS.OCR КОНТЕЙНЕРА")
        print("=" * 35)
        
        # Остановка существующего контейнера
        self.run_command("docker stop dots-ocr-vllm", check=False)
        self.run_command("docker rm dots-ocr-vllm", check=False)
        
        # Путь к кешированной модели
        cache_path = str(self.cache_dir).replace('\\', '/')
        
        # Запуск контейнера с монтированием кеша
        docker_command = f"""
        docker run -d \
            --gpus all \
            --name dots-ocr-vllm \
            --restart unless-stopped \
            -p 8000:8000 \
            -v {cache_path}:/root/.cache/huggingface/hub:ro \
            -e VLLM_GPU_MEMORY_UTILIZATION=0.8 \
            -e VLLM_MAX_MODEL_LEN=4096 \
            -e CUDA_VISIBLE_DEVICES=0 \
            --shm-size=8g \
            vllm/vllm-openai:latest \
            --model rednote-hilab/dots.ocr \
            --trust-remote-code \
            --max-model-len 4096 \
            --gpu-memory-utilization 0.8
        """.strip().replace('\n', ' ').replace('\\', '')
        
        result = self.run_command(docker_command)
        
        if result:
            print("✅ dots.ocr контейнер запущен на порту 8000")
            self.running_containers.append(('dots-ocr-vllm', 8000, 'rednote-hilab/dots.ocr'))
            return True
        else:
            print("❌ Не удалось запустить dots.ocr контейнер")
            return False

    def start_additional_models(self):
        """Запуск дополнительных моделей на разных портах"""
        print("\n🚀 ЗАПУСК ДОПОЛНИТЕЛЬНЫХ МОДЕЛЕЙ")
        print("=" * 40)
        
        port = 8001
        cache_path = str(self.cache_dir).replace('\\', '/')
        
        # Конфигурация для дополнительных моделей
        additional_models = [
            ('got_ocr', 'stepfun-ai/GOT-OCR2_0', 'got-ocr-vllm'),
            ('qwen3_vl', 'Qwen/Qwen3-VL-2B-Instruct', 'qwen3-vl-vllm'),
            ('phi3_vision', 'microsoft/Phi-3.5-vision-instruct', 'phi3-vision-vllm')
        ]
        
        for model_key, model_name, container_name in additional_models:
            if model_key not in self.models_config:
                print(f"⏭️ Пропускаем {model_name} (не найдена)")
                continue
            
            print(f"\n🔄 Запуск {model_name} на порту {port}")
            
            # Остановка существующего контейнера
            self.run_command(f"docker stop {container_name}", check=False)
            self.run_command(f"docker rm {container_name}", check=False)
            
            # Запуск контейнера
            docker_command = f"""
            docker run -d \
                --gpus all \
                --name {container_name} \
                --restart unless-stopped \
                -p {port}:{port} \
                -v {cache_path}:/root/.cache/huggingface/hub:ro \
                -e VLLM_GPU_MEMORY_UTILIZATION=0.6 \
                -e VLLM_MAX_MODEL_LEN=2048 \
                --shm-size=4g \
                vllm/vllm-openai:latest \
                --model {model_name} \
                --trust-remote-code \
                --max-model-len 2048 \
                --gpu-memory-utilization 0.6 \
                --port {port}
            """.strip().replace('\n', ' ').replace('\\', '')
            
            result = self.run_command(docker_command)
            
            if result:
                print(f"✅ {model_name} запущена на порту {port}")
                self.running_containers.append((container_name, port, model_name))
                port += 1
            else:
                print(f"❌ Не удалось запустить {model_name}")

    def wait_for_servers(self):
        """Ожидание запуска всех серверов"""
        print("\n⏳ ОЖИДАНИЕ ЗАПУСКА СЕРВЕРОВ")
        print("=" * 35)
        
        max_attempts = 20
        
        for container_name, port, model_name in self.running_containers:
            print(f"\n🔄 Проверка {model_name} на порту {port}")
            
            for attempt in range(max_attempts):
                try:
                    response = requests.get(f"http://localhost:{port}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {model_name} готова!")
                        break
                except:
                    pass
                
                print(f"⏳ Попытка {attempt + 1}/{max_attempts}...")
                time.sleep(15)
            else:
                print(f"❌ {model_name} не запустилась")
                print(f"📋 Логи контейнера {container_name}:")
                self.run_command(f"docker logs --tail 20 {container_name}")

    def create_unified_client(self):
        """Создание унифицированного клиента для всех моделей"""
        print("\n📝 СОЗДАНИЕ УНИФИЦИРОВАННОГО КЛИЕНТА")
        print("=" * 45)
        
        client_code = f'''#!/usr/bin/env python3
"""
Унифицированный клиент для всех vLLM серверов
Автоматически сгенерирован: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

import requests
import base64
import json
from typing import Dict, Any, Optional

class UnifiedVLLMClient:
    def __init__(self):
        self.servers = {servers_config}
        
    def health_check_all(self) -> Dict[str, bool]:
        """Проверка доступности всех серверов"""
        status = {{}}
        for name, config in self.servers.items():
            try:
                response = requests.get(f"http://localhost:{{config['port']}}/health", timeout=5)
                status[name] = response.status_code == 200
            except:
                status[name] = False
        return status
    
    def process_image(self, image_path: str, model: str = "dots_ocr", 
                     prompt: str = "Extract all text from this image") -> Dict[str, Any]:
        """Обработка изображения выбранной моделью"""
        
        if model not in self.servers:
            return {{"success": False, "error": f"Модель {{model}} недоступна"}}
        
        server_config = self.servers[model]
        port = server_config['port']
        model_name = server_config['model']
        
        try:
            # Кодирование изображения
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Определение MIME типа
            ext = image_path.lower().split('.')[-1]
            mime_type = "image/jpeg" if ext in ['jpg', 'jpeg'] else f"image/{{ext}}"
            
            # Запрос к API
            payload = {{
                "model": model_name,
                "messages": [{{
                    "role": "user",
                    "content": [
                        {{"type": "text", "text": prompt}},
                        {{"type": "image_url", "image_url": {{"url": f"data:{{mime_type}};base64,{{image_base64}}"}}}}
                    ]
                }}],
                "max_tokens": 2048,
                "temperature": 0.1
            }}
            
            response = requests.post(
                f"http://localhost:{{port}}/v1/chat/completions", 
                json=payload, 
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {{
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "model": model_name,
                    "server": model
                }}
            else:
                return {{"success": False, "error": f"HTTP {{response.status_code}}: {{response.text}}"}}
                
        except Exception as e:
            return {{"success": False, "error": str(e)}}
    
    def list_available_models(self) -> Dict[str, Dict]:
        """Список доступных моделей"""
        available = {{}}
        status = self.health_check_all()
        
        for name, config in self.servers.items():
            available[name] = {{
                "model": config['model'],
                "port": config['port'],
                "status": "online" if status.get(name, False) else "offline",
                "description": config.get('description', 'Нет описания')
            }}
        
        return available

# Пример использования
if __name__ == "__main__":
    client = UnifiedVLLMClient()
    
    print("🔍 ПРОВЕРКА ДОСТУПНОСТИ СЕРВЕРОВ")
    print("=" * 40)
    
    models = client.list_available_models()
    for name, info in models.items():
        status_icon = "✅" if info['status'] == 'online' else "❌"
        print(f"{{status_icon}} {{name}}: {{info['model']}} (порт {{info['port']}})")
    
    # Тест с изображением (если есть)
    test_images = ['vllm_test_image.png', 'test_image.png', 'simple_test.png']
    test_image = None
    
    for img in test_images:
        if os.path.exists(img):
            test_image = img
            break
    
    if test_image:
        print(f"\\n🧪 ТЕСТ С ИЗОБРАЖЕНИЕМ: {{test_image}}")
        print("=" * 50)
        
        # Тест с dots.ocr (приоритет)
        if 'dots_ocr' in models and models['dots_ocr']['status'] == 'online':
            print("🔄 Тестируем dots.ocr...")
            result = client.process_image(test_image, 'dots_ocr')
            if result['success']:
                print(f"✅ dots.ocr результат: {{result['content'][:200]}}...")
            else:
                print(f"❌ dots.ocr ошибка: {{result['error']}}")
    else:
        print("\\n⚠️ Тестовые изображения не найдены")
        print("💡 Создайте test_image.png для тестирования")
'''
        
        # Формирование конфигурации серверов
        servers_config = {}
        for container_name, port, model_name in self.running_containers:
            key = container_name.replace('-vllm', '').replace('-', '_')
            servers_config[key] = {
                'port': port,
                'model': model_name,
                'description': f'vLLM сервер для {model_name}'
            }
        
        # Подстановка конфигурации в код
        client_code = client_code.replace('{servers_config}', json.dumps(servers_config, indent=12))
        
        with open('unified_vllm_client.py', 'w', encoding='utf-8') as f:
            f.write(client_code)
        
        print("✅ Унифицированный клиент создан: unified_vllm_client.py")

    def create_management_script(self):
        """Создание скрипта управления контейнерами"""
        print("\n📝 СОЗДАНИЕ СКРИПТА УПРАВЛЕНИЯ")
        print("=" * 35)
        
        management_code = f'''#!/usr/bin/env python3
"""
Скрипт управления vLLM контейнерами
Автоматически сгенерирован: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

import subprocess
import sys

CONTAINERS = {[f'"{name}"' for name, _, _ in self.running_containers]}

def run_command(command):
    """Выполнение команды"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {{e}}")
        return None

def status():
    """Статус всех контейнеров"""
    print("📊 СТАТУС КОНТЕЙНЕРОВ")
    print("=" * 30)
    
    for container in CONTAINERS:
        result = run_command(f"docker ps -f name={{container}} --format 'table {{{{.Names}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}'")
        if result and container in result:
            print(f"✅ {{container}}: Запущен")
        else:
            print(f"❌ {{container}}: Остановлен")

def start_all():
    """Запуск всех контейнеров"""
    print("🚀 ЗАПУСК ВСЕХ КОНТЕЙНЕРОВ")
    print("=" * 30)
    
    for container in CONTAINERS:
        print(f"🔄 Запуск {{container}}...")
        result = run_command(f"docker start {{container}}")
        if result:
            print(f"✅ {{container}} запущен")
        else:
            print(f"❌ Не удалось запустить {{container}}")

def stop_all():
    """Остановка всех контейнеров"""
    print("🛑 ОСТАНОВКА ВСЕХ КОНТЕЙНЕРОВ")
    print("=" * 30)
    
    for container in CONTAINERS:
        print(f"🔄 Остановка {{container}}...")
        result = run_command(f"docker stop {{container}}")
        if result:
            print(f"✅ {{container}} остановлен")
        else:
            print(f"❌ Не удалось остановить {{container}}")

def restart_all():
    """Перезапуск всех контейнеров"""
    print("🔄 ПЕРЕЗАПУСК ВСЕХ КОНТЕЙНЕРОВ")
    print("=" * 30)
    
    stop_all()
    print()
    start_all()

def logs(container_name=None):
    """Просмотр логов"""
    if container_name:
        if container_name in CONTAINERS:
            print(f"📋 ЛОГИ {{container_name}}")
            print("=" * 30)
            run_command(f"docker logs --tail 50 {{container_name}}")
        else:
            print(f"❌ Контейнер {{container_name}} не найден")
    else:
        print("📋 ЛОГИ ВСЕХ КОНТЕЙНЕРОВ")
        print("=" * 30)
        for container in CONTAINERS:
            print(f"\\n--- {{container}} ---")
            run_command(f"docker logs --tail 10 {{container}}")

def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("🔧 УПРАВЛЕНИЕ VLLM КОНТЕЙНЕРАМИ")
        print("=" * 35)
        print("Использование:")
        print("  python manage_vllm.py status     - Статус контейнеров")
        print("  python manage_vllm.py start      - Запуск всех")
        print("  python manage_vllm.py stop       - Остановка всех")
        print("  python manage_vllm.py restart    - Перезапуск всех")
        print("  python manage_vllm.py logs       - Логи всех")
        print("  python manage_vllm.py logs <name> - Логи контейнера")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        status()
    elif command == "start":
        start_all()
    elif command == "stop":
        stop_all()
    elif command == "restart":
        restart_all()
    elif command == "logs":
        container = sys.argv[2] if len(sys.argv) > 2 else None
        logs(container)
    else:
        print(f"❌ Неизвестная команда: {{command}}")

if __name__ == "__main__":
    main()
'''
        
        with open('manage_vllm.py', 'w', encoding='utf-8') as f:
            f.write(management_code)
        
        print("✅ Скрипт управления создан: manage_vllm.py")

    def main(self):
        """Основная функция настройки"""
        print("🚀 КОМПЛЕКСНАЯ НАСТРОЙКА VLLM С КЕШИРОВАННЫМИ МОДЕЛЯМИ")
        print("=" * 70)
        
        # Проверка предварительных требований
        if not self.check_prerequisites():
            print("\n❌ Настройка прервана из-за невыполненных требований")
            sys.exit(1)
        
        # Анализ кешированных моделей
        models = self.analyze_cached_models()
        if not models['ocr'] and not models['vlm']:
            print("\n❌ Подходящие модели не найдены в кеше")
            sys.exit(1)
        
        # Создание конфигурации
        available_models = self.create_vllm_config(models)
        if not available_models:
            print("\n❌ Нет доступных моделей для запуска")
            sys.exit(1)
        
        # Запуск dots.ocr (приоритет)
        dots_ocr_started = self.start_dots_ocr_container()
        
        # Запуск дополнительных моделей
        self.start_additional_models()
        
        if not self.running_containers:
            print("\n❌ Ни один контейнер не был запущен")
            sys.exit(1)
        
        # Ожидание запуска серверов
        self.wait_for_servers()
        
        # Создание клиентских скриптов
        self.create_unified_client()
        self.create_management_script()
        
        # Итоговая информация
        print("\n🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
        print("=" * 30)
        print("📡 Запущенные серверы:")
        for container_name, port, model_name in self.running_containers:
            print(f"   • {model_name} → http://localhost:{port}")
        
        print("\n📋 Созданные файлы:")
        print("   • unified_vllm_client.py - Унифицированный клиент")
        print("   • manage_vllm.py - Управление контейнерами")
        
        print("\n💡 Полезные команды:")
        print("   python unified_vllm_client.py  # Тест всех серверов")
        print("   python manage_vllm.py status   # Статус контейнеров")
        print("   python manage_vllm.py logs     # Просмотр логов")
        
        if dots_ocr_started:
            print("\n🎯 dots.ocr готова к использованию на http://localhost:8000")
        
        print("\n✅ Все кешированные модели подключены к vLLM!")

if __name__ == "__main__":
    setup = VLLMSetup()
    setup.main()