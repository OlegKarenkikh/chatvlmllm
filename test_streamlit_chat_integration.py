#!/usr/bin/env python3
"""
Тест интеграции чата в Streamlit приложении
Проверяем, что запросы из интерфейса доходят до vLLM
"""

import requests
import time
import subprocess
import threading
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def create_test_image():
    """Создаем тестовое изображение"""
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Chat Test Image", fill='black', font=font)
    draw.text((50, 100), "Hello from Streamlit!", fill='black', font=font)
    draw.text((50, 150), "Test-123", fill='black', font=font)
    
    return img

def monitor_container_logs_continuous():
    """Непрерывный мониторинг логов контейнера"""
    print("📋 Начинаем мониторинг логов контейнера...")
    
    try:
        # Запускаем docker logs в режиме follow
        process = subprocess.Popen(
            ["docker", "logs", "dots-ocr-fixed", "--follow", "--tail", "0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("🔍 Ожидаем новые запросы к API...")
        print("💡 Теперь попробуйте отправить сообщение в чате Streamlit")
        print("=" * 60)
        
        request_count = 0
        
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                current_time = time.strftime("%H:%M:%S")
                print(f"[{current_time}] {line.strip()}")
                
                # Считаем запросы к chat/completions
                if "POST /v1/chat/completions" in line:
                    request_count += 1
                    print(f"🎉 ОБНАРУЖЕН ЗАПРОС К CHAT API #{request_count}")
                    print("✅ Промпт и изображение успешно переданы в модель!")
                    
                # Считаем другие типы запросов
                elif "POST" in line and "/v1/" in line:
                    print(f"📤 Другой POST запрос: {line.strip()}")
                elif "GET" in line and ("health" not in line and "models" not in line):
                    print(f"📥 GET запрос: {line.strip()}")
                    
    except KeyboardInterrupt:
        print("\n⏹️ Мониторинг остановлен пользователем")
        process.terminate()
    except Exception as e:
        print(f"❌ Ошибка мониторинга: {e}")

def test_direct_api_call():
    """Тестовый вызов API для сравнения"""
    print("🧪 Выполняем тестовый вызов API для сравнения...")
    
    test_image = create_test_image()
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    payload = {
        "model": "rednote-hilab/dots.ocr",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Что написано на изображении?"
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
        "max_tokens": 1000,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"✅ Тестовый запрос успешен: {content[:100]}...")
        else:
            print(f"❌ Тестовый запрос неудачен: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка тестового запроса: {e}")

def check_streamlit_status():
    """Проверяем статус Streamlit приложения"""
    print("🌐 Проверяем статус Streamlit приложения...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit приложение доступно на http://localhost:8501")
            return True
        else:
            print(f"⚠️ Streamlit отвечает с кодом: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Streamlit недоступен: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Тест интеграции чата в Streamlit")
    print("=" * 60)
    
    # Проверяем статус приложения
    if not check_streamlit_status():
        print("❌ Streamlit приложение недоступно")
        return
    
    # Выполняем тестовый запрос для сравнения
    test_direct_api_call()
    
    print("\n" + "=" * 60)
    print("📋 ИНСТРУКЦИИ ДЛЯ ТЕСТИРОВАНИЯ:")
    print("1. Откройте http://localhost:8501 в браузере")
    print("2. Перейдите в раздел '💬 Режим чата'")
    print("3. Загрузите любое изображение")
    print("4. Отправьте сообщение в чате")
    print("5. Наблюдайте за логами ниже")
    print("=" * 60)
    
    # Запускаем мониторинг логов
    try:
        monitor_container_logs_continuous()
    except KeyboardInterrupt:
        print("\n👋 Тестирование завершено")

if __name__ == "__main__":
    main()