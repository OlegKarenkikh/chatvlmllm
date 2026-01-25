#!/usr/bin/env python3
"""
Восстановление рабочей конфигурации dots.ocr с 8192 токенами
"""

import subprocess
import time
import requests

def restore_working_dots_ocr():
    """Восстановление рабочей конфигурации dots.ocr"""
    
    print("🔄 Восстановление рабочей конфигурации dots.ocr")
    print("=" * 50)
    
    # Получаем путь к кешу
    try:
        userprofile = subprocess.check_output(['echo', '%USERPROFILE%'], shell=True, text=True).strip()
        cache_path = f"{userprofile}/.cache/huggingface/hub"
    except:
        cache_path = "~/.cache/huggingface/hub"
    
    print(f"📁 Путь к кешу: {cache_path}")
    
    # Рабочая конфигурация dots.ocr (как было раньше)
    command = [
        "docker", "run", "-d",
        "--name", "dots-ocr-vllm-optimized",
        "--restart", "unless-stopped",
        "-p", "8000:8000",
        "--gpus", "all",
        "--shm-size", "8g",
        "-v", f"{cache_path}:/root/.cache/huggingface/hub:rw",
        "-v", f"{cache_path}:/home/vllm/.cache/huggingface/hub:rw",
        "-e", "HF_HOME=/root/.cache/huggingface",
        "-e", "TRANSFORMERS_CACHE=/root/.cache/huggingface/hub",
        "-e", "HF_HUB_CACHE=/root/.cache/huggingface/hub",
        "-e", "CUDA_VISIBLE_DEVICES=0",
        "-e", "NVIDIA_VISIBLE_DEVICES=all",
        "vllm/vllm-openai:latest",
        "--model", "rednote-hilab/dots.ocr",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--trust-remote-code",
        "--max-model-len", "8192",  # Как было раньше
        "--gpu-memory-utilization", "0.85",  # Как было раньше
        "--dtype", "bfloat16",
        "--enforce-eager",
        "--disable-log-requests"
    ]
    
    print("🚀 Запуск dots.ocr с проверенными настройками...")
    print("   - Модель: rednote-hilab/dots.ocr")
    print("   - Макс. токенов: 8192")
    print("   - GPU утилизация: 85%")
    print("   - Режим: eager")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Контейнер запущен успешно")
        else:
            print(f"❌ Ошибка запуска: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    print("⏳ Ожидание готовности dots.ocr...")
    
    # Ожидание готовности (до 5 минут)
    max_wait = 300
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check прошел")
                
                # Проверяем API моделей
                models_response = requests.get("http://localhost:8000/v1/models", timeout=5)
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    for model in models_data.get("data", []):
                        print(f"✅ Модель готова: {model['id']}")
                        print(f"   Макс. токенов: {model.get('max_model_len', 'N/A')}")
                    return True
                else:
                    print("⏳ API моделей еще не готов...")
            else:
                print("⏳ Health check не прошел...")
        except Exception as e:
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0:  # Каждые 30 секунд
                print(f"⏳ Ожидание... ({elapsed}s)")
        
        time.sleep(5)
    
    print("❌ dots.ocr не готов после 5 минут")
    return False

def test_working_ocr():
    """Тест рабочей OCR"""
    print("\n🧪 Тестирование восстановленной OCR...")
    
    # Создаем тестовое изображение
    from PIL import Image, ImageDraw, ImageFont
    import base64
    import io
    
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Working OCR Test", fill='black', font=font)
    draw.text((50, 100), "8192 tokens context", fill='blue', font=font)
    draw.text((50, 150), "Restored configuration", fill='green', font=font)
    
    # Сохраняем изображение
    img.save("test_working_ocr.png")
    
    # Конвертируем в base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Тестируем API
    payload = {
        "model": "rednote-hilab/dots.ocr",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract all text from this image"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        }],
        "max_tokens": 1024,
        "temperature": 0.1
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            timeout=60
        )
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens", 0)
            
            print(f"✅ OCR тест успешен!")
            print(f"   Время: {processing_time:.1f}с")
            print(f"   Токенов: {tokens_used}")
            print(f"   Результат: {content}")
            
            return True
        else:
            print(f"❌ API ошибка: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

def main():
    """Основная функция"""
    print("🔄 ВОССТАНОВЛЕНИЕ РАБОЧЕЙ КОНФИГУРАЦИИ DOTS.OCR")
    print("=" * 60)
    
    # 1. Восстановление dots.ocr
    success = restore_working_dots_ocr()
    
    if not success:
        print("\n❌ Не удалось восстановить рабочую конфигурацию")
        print("💡 Проверьте логи: docker logs dots-ocr-vllm-optimized")
        return False
    
    # 2. Тестирование
    test_success = test_working_ocr()
    
    # 3. Итоговый статус
    print(f"\n📊 ИТОГОВЫЙ СТАТУС:")
    print("=" * 60)
    
    if success and test_success:
        print("🎉 РАБОЧАЯ КОНФИГУРАЦИЯ ВОССТАНОВЛЕНА!")
        print("✅ dots.ocr работает с 8192 токенами")
        print("✅ OCR тест прошел успешно")
        print("💡 Система готова к работе")
        print("🚀 Запуск приложения: streamlit run app.py")
        
        # Проверяем статус контейнера
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=dots-ocr-vllm-optimized", "--format", "{{.Status}}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                status = result.stdout.strip()
                print(f"📊 Статус контейнера: {status}")
        except:
            pass
        
        return True
    else:
        print("❌ ВОССТАНОВЛЕНИЕ НЕ УДАЛОСЬ")
        if not success:
            print("   - Контейнер не запустился")
        if not test_success:
            print("   - OCR тест не прошел")
        return False

if __name__ == "__main__":
    main()