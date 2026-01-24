#!/usr/bin/env python3
"""
Исправление проблем с vLLM контейнерами
"""

import subprocess
import time
import requests
import sys
import os

def run_command(command, shell=True, check=True):
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

def stop_all_containers():
    """Остановка всех vLLM контейнеров"""
    print("🛑 ОСТАНОВКА ВСЕХ КОНТЕЙНЕРОВ")
    print("=" * 35)
    
    containers = ["dots-ocr-vllm", "got-ocr-vllm", "qwen3-vl-vllm", "phi3-vision-vllm"]
    
    for container in containers:
        print(f"🔄 Остановка {container}...")
        run_command(f"docker stop {container}", check=False)
        run_command(f"docker rm {container}", check=False)

def create_fixed_dockerfile():
    """Создание исправленного Dockerfile с необходимыми пакетами"""
    print("\n📝 СОЗДАНИЕ ИСПРАВЛЕННОГО DOCKERFILE")
    print("=" * 45)
    
    dockerfile_content = '''FROM vllm/vllm-openai:latest

# Установка недостающих пакетов
RUN pip install verovio

# Создание рабочей директории
WORKDIR /app

# Копирование скриптов запуска
COPY start_server.sh /app/start_server.sh
RUN chmod +x /app/start_server.sh

ENTRYPOINT ["/app/start_server.sh"]
'''
    
    with open('Dockerfile.vllm-fixed', 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    # Создание скрипта запуска
    start_script = '''#!/bin/bash
set -e

echo "Starting vLLM server..."
echo "Model: $MODEL_NAME"
echo "Port: $PORT"
echo "Max tokens: $MAX_TOKENS"
echo "GPU utilization: $GPU_UTIL"

# Start vLLM server
exec vllm serve "$MODEL_NAME" \\
    --port "$PORT" \\
    --trust-remote-code \\
    --max-model-len "$MAX_TOKENS" \\
    --gpu-memory-utilization "$GPU_UTIL" \\
    --host 0.0.0.0
'''
    
    with open('start_server.sh', 'w', encoding='utf-8') as f:
        f.write(start_script)
    
    print("✅ Dockerfile и скрипт запуска созданы")

def build_fixed_image():
    """Сборка исправленного образа"""
    print("\n🔨 СБОРКА ИСПРАВЛЕННОГО ОБРАЗА")
    print("=" * 35)
    
    result = run_command("docker build -f Dockerfile.vllm-fixed -t vllm-fixed:latest .")
    
    if result:
        print("✅ Исправленный образ собран")
        return True
    else:
        print("❌ Не удалось собрать образ")
        return False

def start_fixed_containers():
    """Запуск исправленных контейнеров"""
    print("\n🚀 ЗАПУСК ИСПРАВЛЕННЫХ КОНТЕЙНЕРОВ")
    print("=" * 40)
    
    cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
    
    # Конфигурация контейнеров
    containers_config = [
        {
            'name': 'dots-ocr-vllm-fixed',
            'model': 'rednote-hilab/dots.ocr',
            'port': 8000,
            'max_tokens': 4096,
            'gpu_util': 0.7
        },
        {
            'name': 'qwen3-vl-vllm-fixed',
            'model': 'Qwen/Qwen3-VL-2B-Instruct',
            'port': 8002,
            'max_tokens': 2048,
            'gpu_util': 0.5
        },
        {
            'name': 'phi3-vision-vllm-fixed',
            'model': 'microsoft/Phi-3.5-vision-instruct',
            'port': 8003,
            'max_tokens': 2048,
            'gpu_util': 0.5
        }
    ]
    
    # Пропускаем GOT-OCR пока не решим проблему с verovio
    
    for config in containers_config:
        print(f"\n🔄 Запуск {config['name']}...")
        
        docker_command = f"""
        docker run -d \\
            --gpus all \\
            --name {config['name']} \\
            --restart unless-stopped \\
            -p {config['port']}:{config['port']} \\
            -v {cache_path}:/root/.cache/huggingface/hub:ro \\
            -e MODEL_NAME="{config['model']}" \\
            -e PORT={config['port']} \\
            -e MAX_TOKENS={config['max_tokens']} \\
            -e GPU_UTIL={config['gpu_util']} \\
            --shm-size=8g \\
            vllm-fixed:latest
        """.strip().replace('\n', ' ').replace('\\', '')
        
        result = run_command(docker_command)
        
        if result:
            print(f"✅ {config['name']} запущен на порту {config['port']}")
        else:
            print(f"❌ Не удалось запустить {config['name']}")

def wait_for_servers():
    """Ожидание запуска серверов"""
    print("\n⏳ ОЖИДАНИЕ ЗАПУСКА СЕРВЕРОВ")
    print("=" * 35)
    
    ports = [8000, 8002, 8003]
    max_attempts = 30
    
    for port in ports:
        print(f"\n🔄 Проверка сервера на порту {port}")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Сервер на порту {port} готов!")
                    break
            except:
                pass
            
            print(f"⏳ Попытка {attempt + 1}/{max_attempts}...")
            time.sleep(15)
        else:
            print(f"❌ Сервер на порту {port} не запустился")

def create_simple_client():
    """Создание простого клиента для тестирования"""
    print("\n📝 СОЗДАНИЕ ПРОСТОГО КЛИЕНТА")
    print("=" * 35)
    
    client_code = '''#!/usr/bin/env python3
"""
Простой клиент для тестирования исправленных vLLM серверов
"""

import requests
import base64
import json
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Создание тестового изображения"""
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 80), "HELLO WORLD", fill='black', font=font)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def test_server(port, model_name):
    """Тест сервера"""
    print(f"\\n🧪 Тестируем сервер на порту {port}")
    
    try:
        # Проверка health
        health_response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if health_response.status_code != 200:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
        
        print("✅ Health check прошел")
        
        # Создание тестового изображения
        image_base64 = create_test_image()
        
        # Отправка запроса
        payload = {
            "model": model_name,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all text from this image"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 100
        }
        
        response = requests.post(
            f"http://localhost:{port}/v1/chat/completions",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"✅ OCR результат: {content}")
            return True
        else:
            print(f"❌ API ошибка: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция"""
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕННЫХ СЕРВЕРОВ")
    print("=" * 45)
    
    servers = [
        (8000, "rednote-hilab/dots.ocr"),
        (8002, "Qwen/Qwen3-VL-2B-Instruct"),
        (8003, "microsoft/Phi-3.5-vision-instruct")
    ]
    
    working_servers = 0
    
    for port, model in servers:
        if test_server(port, model):
            working_servers += 1
    
    print(f"\\n📊 РЕЗУЛЬТАТ: {working_servers}/{len(servers)} серверов работают")
    
    if working_servers > 0:
        print("🎉 Система частично функциональна!")
    else:
        print("❌ Все серверы недоступны")

if __name__ == "__main__":
    main()
'''
    
    with open('test_fixed_servers.py', 'w', encoding='utf-8') as f:
        f.write(client_code)
    
    print("✅ Клиент создан: test_fixed_servers.py")

def main():
    """Основная функция исправления"""
    print("🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМ VLLM КОНТЕЙНЕРОВ")
    print("=" * 50)
    
    # Остановка существующих контейнеров
    stop_all_containers()
    
    # Создание исправленного Dockerfile
    create_fixed_dockerfile()
    
    # Сборка исправленного образа
    if not build_fixed_image():
        print("\n❌ Не удалось собрать исправленный образ")
        sys.exit(1)
    
    # Запуск исправленных контейнеров
    start_fixed_containers()
    
    # Ожидание запуска
    wait_for_servers()
    
    # Создание клиента
    create_simple_client()
    
    print("\n🎉 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
    print("=" * 30)
    print("📋 Созданные файлы:")
    print("   • Dockerfile.vllm-fixed - Исправленный образ")
    print("   • start_server.sh - Скрипт запуска")
    print("   • test_fixed_servers.py - Клиент для тестирования")
    print()
    print("💡 Следующие шаги:")
    print("   1. Дождитесь полной загрузки серверов (5-10 минут)")
    print("   2. Запустите: python test_fixed_servers.py")
    print("   3. Проверьте логи: docker logs <container_name>")

if __name__ == "__main__":
    main()