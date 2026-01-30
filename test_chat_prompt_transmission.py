#!/usr/bin/env python3
"""
Тест передачи промптов и изображений в режиме чата
Проверяем, что запросы доходят до vLLM API
"""

import requests
import base64
import json
import time
from PIL import Image
import io

def test_vllm_api_direct():
    """Прямой тест vLLM API"""
    print("🔍 Тестируем прямое подключение к vLLM API...")
    
    # Проверяем health
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Health check: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Проверяем модели
    try:
        models_response = requests.get("http://localhost:8000/v1/models", timeout=5)
        models_data = models_response.json()
        print(f"✅ Models available: {len(models_data.get('data', []))}")
        for model in models_data.get('data', []):
            print(f"   - {model.get('id', 'unknown')}")
    except Exception as e:
        print(f"❌ Models check failed: {e}")
        return False
    
    return True

def create_test_image():
    """Создаем простое тестовое изображение"""
    print("🖼️ Создаем тестовое изображение...")
    
    # Создаем простое изображение с текстом
    from PIL import Image, ImageDraw, ImageFont
    
    # Создаем белое изображение
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Добавляем текст
    try:
        # Пытаемся использовать системный шрифт
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback на стандартный шрифт
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Hello World!", fill='black', font=font)
    draw.text((50, 100), "Test Document", fill='black', font=font)
    draw.text((50, 150), "123-456-789", fill='black', font=font)
    
    return img

def image_to_base64(image):
    """Конвертируем изображение в base64"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def test_vllm_chat_completion():
    """Тест chat completion API с изображением"""
    print("💬 Тестируем chat completion с изображением...")
    
    # Создаем тестовое изображение
    test_image = create_test_image()
    image_base64 = image_to_base64(test_image)
    
    # Подготавливаем запрос
    url = "http://localhost:8000/v1/chat/completions"
    
    payload = {
        "model": "rednote-hilab/dots.ocr",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Извлеки весь текст из этого изображения."
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
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"📤 Отправляем запрос к {url}")
    print(f"📝 Промпт: {payload['messages'][0]['content'][0]['text']}")
    print(f"🖼️ Изображение: {len(image_base64)} символов base64")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        processing_time = time.time() - start_time
        
        print(f"⏱️ Время обработки: {processing_time:.2f}с")
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"✅ Успешный ответ:")
            print(f"📄 Содержимое: {content[:200]}...")
            
            # Проверяем, что модель действительно распознала текст
            if any(word in content.lower() for word in ['hello', 'world', 'test', 'document', '123']):
                print("✅ Модель корректно распознала текст из изображения!")
                return True
            else:
                print("⚠️ Модель не распознала ожидаемый текст")
                return False
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса (60 сек)")
        return False
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def test_vllm_streamlit_adapter():
    """Тест VLLMStreamlitAdapter"""
    print("🔧 Тестируем VLLMStreamlitAdapter...")
    
    try:
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        
        adapter = VLLMStreamlitAdapter()
        test_image = create_test_image()
        
        print("📤 Отправляем запрос через адаптер...")
        
        start_time = time.time()
        result = adapter.process_image(
            image=test_image,
            prompt="Извлеки весь текст из этого изображения.",
            model="rednote-hilab/dots.ocr",
            max_tokens=1000
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️ Время обработки: {processing_time:.2f}с")
        
        if result and result.get("success"):
            print("✅ Адаптер работает корректно!")
            print(f"📄 Результат: {result['text'][:200]}...")
            return True
        else:
            print(f"❌ Ошибка адаптера: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка импорта/выполнения адаптера: {e}")
        return False

def monitor_container_logs():
    """Мониторим логи контейнера во время тестов"""
    print("📋 Проверяем логи контейнера...")
    
    import subprocess
    
    try:
        # Получаем последние логи
        result = subprocess.run(
            ["docker", "logs", "dots-ocr-fixed", "--tail", "10"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("📋 Последние логи контейнера:")
            print(result.stdout)
            return True
        else:
            print(f"❌ Ошибка получения логов: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка мониторинга логов: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Начинаем тестирование передачи промптов и изображений...")
    print("=" * 60)
    
    # Тест 1: Прямое подключение к API
    print("\n1️⃣ Тест прямого подключения к vLLM API")
    api_ok = test_vllm_api_direct()
    
    if not api_ok:
        print("❌ API недоступен, дальнейшие тесты невозможны")
        return
    
    # Тест 2: Мониторинг логов до запроса
    print("\n2️⃣ Логи контейнера до запроса")
    monitor_container_logs()
    
    # Тест 3: Прямой запрос к chat completion
    print("\n3️⃣ Тест chat completion API")
    chat_ok = test_vllm_chat_completion()
    
    # Тест 4: Мониторинг логов после запроса
    print("\n4️⃣ Логи контейнера после запроса")
    monitor_container_logs()
    
    # Тест 5: Тест через адаптер
    print("\n5️⃣ Тест VLLMStreamlitAdapter")
    adapter_ok = test_vllm_streamlit_adapter()
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ:")
    print(f"   🔗 API подключение: {'✅' if api_ok else '❌'}")
    print(f"   💬 Chat completion: {'✅' if chat_ok else '❌'}")
    print(f"   🔧 Streamlit адаптер: {'✅' if adapter_ok else '❌'}")
    
    if api_ok and chat_ok and adapter_ok:
        print("\n🎉 Все тесты прошли успешно! Передача промптов и изображений работает корректно.")
    else:
        print("\n⚠️ Обнаружены проблемы с передачей данных.")
        
        if not chat_ok:
            print("💡 Рекомендации:")
            print("   - Проверьте, что контейнер dots-ocr-fixed полностью загружен")
            print("   - Убедитесь, что модель готова к обработке запросов")
            print("   - Проверьте логи контейнера на наличие ошибок")

if __name__ == "__main__":
    main()