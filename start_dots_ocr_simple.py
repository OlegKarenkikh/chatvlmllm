#!/usr/bin/env python3
"""
Простой запуск только dots.ocr с исправлениями
"""

import subprocess
import time
import requests
import os

def run_command(command):
    """Выполнение команды"""
    print(f"🔄 {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        if e.stderr:
            print(f"❌ {e.stderr}")
        return False

def main():
    """Основная функция"""
    print("🚀 ПРОСТОЙ ЗАПУСК DOTS.OCR")
    print("=" * 30)
    
    # Остановка существующих контейнеров
    print("🛑 Остановка существующих контейнеров...")
    run_command("docker stop dots-ocr-vllm")
    run_command("docker rm dots-ocr-vllm")
    
    # Путь к кешу
    cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
    print(f"📁 Путь к кешу: {cache_path}")
    
    # Запуск dots.ocr с упрощенными параметрами
    print("\n🚀 Запуск dots.ocr...")
    
    docker_command = f"""
    docker run -d \
        --gpus all \
        --name dots-ocr-simple \
        --restart unless-stopped \
        -p 8000:8000 \
        -v {cache_path}:/root/.cache/huggingface/hub:ro \
        --shm-size=8g \
        vllm/vllm-openai:latest \
        --model rednote-hilab/dots.ocr \
        --trust-remote-code \
        --max-model-len 2048 \
        --gpu-memory-utilization 0.6 \
        --host 0.0.0.0 \
        --port 8000
    """.strip().replace('\n', ' ').replace('\\', '')
    
    if run_command(docker_command):
        print("✅ dots.ocr контейнер запущен")
        
        # Ожидание запуска
        print("\n⏳ Ожидание запуска сервера...")
        max_attempts = 20
        
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ dots.ocr готова к работе!")
                    
                    # Проверка models endpoint
                    try:
                        models_response = requests.get("http://localhost:8000/v1/models", timeout=5)
                        if models_response.status_code == 200:
                            models_data = models_response.json()
                            print(f"📊 Доступные модели: {len(models_data.get('data', []))}")
                            for model in models_data.get('data', []):
                                print(f"   • {model.get('id', 'unknown')}")
                    except Exception as e:
                        print(f"⚠️ Не удалось получить список моделей: {e}")
                    
                    break
            except:
                pass
            
            print(f"⏳ Попытка {attempt + 1}/{max_attempts}...")
            time.sleep(15)
        else:
            print("❌ Сервер не запустился в течение 5 минут")
            print("📋 Проверьте логи: docker logs dots-ocr-simple")
            return
        
        # Создание простого тестового клиента
        print("\n📝 Создание тестового клиента...")
        
        test_client = '''#!/usr/bin/env python3
"""
Простой тест dots.ocr
"""

import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Создание тестового изображения"""
    img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 30), "HELLO WORLD", fill='black', font=font)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def test_dots_ocr():
    """Тест dots.ocr"""
    print("🧪 ТЕСТ DOTS.OCR")
    print("=" * 20)
    
    try:
        # Health check
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Health check прошел")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return
        
        # Создание тестового изображения
        image_base64 = create_test_image()
        print("✅ Тестовое изображение создано")
        
        # OCR запрос
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all text from this image"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 100,
            "temperature": 0.1
        }
        
        print("🔄 Отправка OCR запроса...")
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
            else:
                print("⚠️ Текст распознан не полностью")
        else:
            print(f"❌ API ошибка: {response.status_code}")
            print(f"❌ Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_dots_ocr()
'''
        
        with open('test_dots_ocr_simple.py', 'w', encoding='utf-8') as f:
            f.write(test_client)
        
        print("✅ Тестовый клиент создан: test_dots_ocr_simple.py")
        
        print("\n🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
        print("=" * 25)
        print("📡 dots.ocr доступна на: http://localhost:8000")
        print("🧪 Запустите тест: python test_dots_ocr_simple.py")
        print("📋 Логи: docker logs dots-ocr-simple")
        
    else:
        print("❌ Не удалось запустить контейнер")

if __name__ == "__main__":
    main()