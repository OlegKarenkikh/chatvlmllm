#!/usr/bin/env python3
"""
Автоматическая настройка dots.ocr через vLLM Docker в WSL
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

def check_prerequisites():
    """Проверка предварительных требований"""
    print("🔍 ПРОВЕРКА ПРЕДВАРИТЕЛЬНЫХ ТРЕБОВАНИЙ")
    print("=" * 50)
    
    # Проверка WSL
    result = run_command("wsl --version", check=False)
    if result is None:
        print("❌ WSL не установлен или недоступен")
        return False
    
    # Проверка Docker
    result = run_command("docker --version", check=False)
    if result is None:
        print("❌ Docker не установлен")
        print("💡 Установите Docker Desktop или Docker в WSL")
        return False
    
    # Проверка NVIDIA драйвера
    result = run_command("nvidia-smi", check=False)
    if result is None:
        print("❌ NVIDIA драйвер недоступен")
        return False
    
    # Проверка GPU в Docker
    result = run_command("docker run --rm --gpus all nvidia/cuda:12.8-base-ubuntu22.04 nvidia-smi", check=False)
    if result is None:
        print("❌ GPU недоступен в Docker")
        print("💡 Установите nvidia-container-toolkit")
        return False
    
    print("✅ Все предварительные требования выполнены")
    return True

def pull_dots_ocr_image():
    """Загрузка Docker образа dots.ocr"""
    print("\n🐳 ЗАГРУЗКА DOCKER ОБРАЗА")
    print("=" * 30)
    
    image_name = "rednotehilab/dots.ocr:vllm-openai-v0.9.1"
    
    print(f"📥 Загружаем образ: {image_name}")
    result = run_command(f"docker pull {image_name}")
    
    if result:
        print("✅ Docker образ загружен успешно")
        return True
    else:
        print("❌ Не удалось загрузить Docker образ")
        return False

def start_dots_ocr_container():
    """Запуск контейнера dots.ocr"""
    print("\n🚀 ЗАПУСК КОНТЕЙНЕРА")
    print("=" * 25)
    
    # Остановка существующего контейнера
    print("🛑 Остановка существующего контейнера...")
    run_command("docker stop dots-ocr-server", check=False)
    run_command("docker rm dots-ocr-server", check=False)
    
    # Запуск нового контейнера
    docker_command = """
    docker run -d \
        --gpus all \
        --name dots-ocr-server \
        --restart unless-stopped \
        -p 8000:8000 \
        -e VLLM_GPU_MEMORY_UTILIZATION=0.9 \
        -e VLLM_MAX_MODEL_LEN=4096 \
        -e CUDA_VISIBLE_DEVICES=0 \
        --shm-size=8g \
        rednotehilab/dots.ocr:vllm-openai-v0.9.1
    """.strip().replace('\n', ' ').replace('\\', '')
    
    result = run_command(docker_command)
    
    if result:
        print("✅ Контейнер запущен")
        return True
    else:
        print("❌ Не удалось запустить контейнер")
        return False

def wait_for_server():
    """Ожидание запуска сервера"""
    print("\n⏳ ОЖИДАНИЕ ЗАПУСКА СЕРВЕРА")
    print("=" * 35)
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Сервер запущен и готов к работе!")
                return True
        except:
            pass
        
        print(f"⏳ Попытка {attempt + 1}/{max_attempts}...")
        time.sleep(10)
    
    print("❌ Сервер не запустился в течение 5 минут")
    print("📋 Логи контейнера:")
    run_command("docker logs dots-ocr-server")
    return False

def test_ocr_functionality():
    """Тест функциональности OCR"""
    print("\n🧪 ТЕСТ ФУНКЦИОНАЛЬНОСТИ")
    print("=" * 30)
    
    # Создание тестового изображения
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Создаем простое изображение с текстом
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 80), "HELLO WORLD TEST", fill='black', font=font)
        img.save('vllm_test_image.png')
        
        print("✅ Тестовое изображение создано")
        
    except Exception as e:
        print(f"⚠️ Не удалось создать тестовое изображение: {e}")
        return False
    
    # Тест API
    try:
        import base64
        
        # Кодирование изображения
        with open('vllm_test_image.png', 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Запрос к API
        payload = {
            "model": "dots.ocr",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this image"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 100
        }
        
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"✅ OCR результат: {content}")
            
            if "HELLO" in content.upper():
                print("🎉 Тест прошел успешно!")
                return True
            else:
                print("⚠️ Текст не распознан корректно")
                return False
        else:
            print(f"❌ API ошибка: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def create_client_script():
    """Создание клиентского скрипта"""
    print("\n📝 СОЗДАНИЕ КЛИЕНТСКОГО СКРИПТА")
    print("=" * 40)
    
    client_code = '''#!/usr/bin/env python3
"""
Клиент для dots.ocr vLLM сервера
"""

import requests
import base64
import json
from typing import Dict, Any

class DotsOCRVLLMClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self) -> bool:
        """Проверка доступности сервера"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def process_image(self, image_path: str, prompt: str = "Extract all text") -> Dict[str, Any]:
        """Обработка изображения"""
        try:
            # Кодирование изображения
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Запрос к API
            payload = {
                "model": "dots.ocr",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                "max_tokens": 2048
            }
            
            response = requests.post(f"{self.base_url}/v1/chat/completions", json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "model": "dots.ocr-vllm"
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

# Пример использования
if __name__ == "__main__":
    client = DotsOCRVLLMClient()
    
    if client.health_check():
        print("✅ Сервер доступен")
        
        # Тест с изображением
        result = client.process_image("vllm_test_image.png")
        if result["success"]:
            print(f"📝 Результат: {result['content']}")
        else:
            print(f"❌ Ошибка: {result['error']}")
    else:
        print("❌ Сервер недоступен")
'''
    
    with open('vllm_dots_ocr_client.py', 'w', encoding='utf-8') as f:
        f.write(client_code)
    
    print("✅ Клиентский скрипт создан: vllm_dots_ocr_client.py")

def main():
    """Основная функция настройки"""
    print("🚀 АВТОМАТИЧЕСКАЯ НАСТРОЙКА DOTS.OCR ЧЕРЕЗ VLLM DOCKER")
    print("=" * 70)
    
    # Проверка предварительных требований
    if not check_prerequisites():
        print("\n❌ Настройка прервана из-за невыполненных требований")
        sys.exit(1)
    
    # Загрузка Docker образа
    if not pull_dots_ocr_image():
        print("\n❌ Настройка прервана - не удалось загрузить образ")
        sys.exit(1)
    
    # Запуск контейнера
    if not start_dots_ocr_container():
        print("\n❌ Настройка прервана - не удалось запустить контейнер")
        sys.exit(1)
    
    # Ожидание запуска сервера
    if not wait_for_server():
        print("\n❌ Настройка прервана - сервер не запустился")
        sys.exit(1)
    
    # Тест функциональности
    if not test_ocr_functionality():
        print("\n⚠️ Сервер запущен, но тест OCR не прошел")
    
    # Создание клиентского скрипта
    create_client_script()
    
    # Итоговая информация
    print("\n🎉 НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 40)
    print("📡 API доступно на: http://localhost:8000")
    print("📋 Документация: http://localhost:8000/docs")
    print("🐍 Клиент: vllm_dots_ocr_client.py")
    print("\n📋 Полезные команды:")
    print("  docker logs dots-ocr-server  # Просмотр логов")
    print("  docker stop dots-ocr-server  # Остановка сервера")
    print("  docker start dots-ocr-server # Запуск сервера")
    
    print("\n✅ dots.ocr готова к использованию через vLLM!")

if __name__ == "__main__":
    main()