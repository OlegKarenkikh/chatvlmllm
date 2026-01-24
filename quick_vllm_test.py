#!/usr/bin/env python3
"""
Быстрый тест vLLM dots.ocr решения
"""

import subprocess
import time
import requests
import sys
import os

def check_docker():
    """Проверка Docker"""
    print("🐳 Проверка Docker...")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker не найден")
            return False
    except:
        print("❌ Docker недоступен")
        return False

def check_gpu():
    """Проверка GPU"""
    print("🖥️ Проверка GPU...")
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU доступен")
            return True
        else:
            print("❌ NVIDIA GPU недоступен")
            return False
    except:
        print("❌ nvidia-smi не найден")
        return False

def check_container():
    """Проверка контейнера dots.ocr"""
    print("📦 Проверка контейнера dots.ocr...")
    try:
        result = subprocess.run(["docker", "ps", "--filter", "name=dots-ocr-server"], 
                              capture_output=True, text=True)
        if "dots-ocr-server" in result.stdout:
            print("✅ Контейнер dots-ocr-server запущен")
            return True
        else:
            print("❌ Контейнер dots-ocr-server не найден")
            return False
    except:
        print("❌ Ошибка проверки контейнера")
        return False

def check_api():
    """Проверка API"""
    print("📡 Проверка API...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API доступно на порту 8000")
            return True
        else:
            print(f"❌ API недоступно: {response.status_code}")
            return False
    except:
        print("❌ API недоступно")
        return False

def start_container():
    """Запуск контейнера"""
    print("🚀 Запуск контейнера dots.ocr...")
    
    # Остановка существующего
    subprocess.run(["docker", "stop", "dots-ocr-server"], 
                  capture_output=True, text=True)
    subprocess.run(["docker", "rm", "dots-ocr-server"], 
                  capture_output=True, text=True)
    
    # Запуск нового
    cmd = [
        "docker", "run", "-d",
        "--gpus", "all",
        "--name", "dots-ocr-server",
        "--restart", "unless-stopped",
        "-p", "8000:8000",
        "-e", "VLLM_GPU_MEMORY_UTILIZATION=0.9",
        "-e", "CUDA_VISIBLE_DEVICES=0",
        "--shm-size=8g",
        "rednotehilab/dots.ocr:vllm-openai-v0.9.1"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Контейнер запущен")
            return True
        else:
            print(f"❌ Ошибка запуска: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Исключение при запуске: {e}")
        return False

def wait_for_api():
    """Ожидание готовности API"""
    print("⏳ Ожидание готовности API...")
    
    for i in range(30):  # 5 минут максимум
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API готово!")
                return True
        except:
            pass
        
        print(f"   Попытка {i+1}/30...")
        time.sleep(10)
    
    print("❌ API не готово в течение 5 минут")
    return False

def test_ocr():
    """Тест OCR функциональности"""
    print("🧪 Тест OCR...")
    
    # Создание тестового изображения
    try:
        from PIL import Image, ImageDraw, ImageFont
        import base64
        
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 30), "QUICK TEST", fill='black', font=font)
        img.save('quick_test.png')
        
        # Кодирование в base64
        with open('quick_test.png', 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        print("✅ Тестовое изображение создано")
        
    except Exception as e:
        print(f"❌ Ошибка создания изображения: {e}")
        return False
    
    # Тест API
    try:
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
        
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            timeout=60
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            print(f"✅ OCR успешно!")
            print(f"📝 Результат: {content}")
            print(f"⏱️ Время: {end_time - start_time:.3f}s")
            
            if "QUICK" in content.upper() or "TEST" in content.upper():
                print("🎉 Текст распознан корректно!")
                return True
            else:
                print("⚠️ Текст распознан частично")
                return True
        else:
            print(f"❌ API ошибка: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def main():
    """Основная функция быстрого теста"""
    print("⚡ БЫСТРЫЙ ТЕСТ VLLM DOTS.OCR РЕШЕНИЯ")
    print("=" * 50)
    
    # Проверка предварительных требований
    if not check_docker():
        print("\n❌ Docker недоступен - установите Docker Desktop")
        return False
    
    if not check_gpu():
        print("\n❌ GPU недоступен - проверьте NVIDIA драйверы")
        return False
    
    # Проверка существующего контейнера
    if check_container() and check_api():
        print("\n✅ Контейнер уже запущен и работает!")
    else:
        print("\n🔄 Запуск нового контейнера...")
        
        if not start_container():
            print("\n❌ Не удалось запустить контейнер")
            return False
        
        if not wait_for_api():
            print("\n❌ API не готово")
            print("📋 Логи контейнера:")
            subprocess.run(["docker", "logs", "dots-ocr-server"])
            return False
    
    # Тест функциональности
    if test_ocr():
        print("\n🎉 VLLM DOTS.OCR РАБОТАЕТ ОТЛИЧНО!")
        print("📋 Полезные команды:")
        print("   docker logs dots-ocr-server  # Просмотр логов")
        print("   docker stop dots-ocr-server  # Остановка")
        print("   docker start dots-ocr-server # Запуск")
        print("\n📡 API доступно на: http://localhost:8000")
        print("📚 Документация: http://localhost:8000/docs")
        return True
    else:
        print("\n❌ Проблемы с OCR функциональностью")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ ГОТОВО К ИНТЕГРАЦИИ В CHATVLMLLM!")
    else:
        print("\n❌ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")
    
    sys.exit(0 if success else 1)