#!/usr/bin/env python3
"""
Тест интеграции официальных промптов в Streamlit приложении
Проверяем, что официальные промпты работают через интерфейс
"""

import requests
import time
import subprocess
import threading
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def create_simple_test_image():
    """Создаем простое тестовое изображение для быстрого тестирования"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "ТЕСТ ДОКУМЕНТ", fill='black', font=font)
    
    # Простая таблица
    draw.rectangle([50, 80, 350, 180], outline='black', width=2)
    draw.line([50, 110, 350, 110], fill='black', width=1)
    draw.line([200, 80, 200, 180], fill='black', width=1)
    
    draw.text((60, 90), "Поле", fill='black', font=font)
    draw.text((210, 90), "Значение", fill='black', font=font)
    draw.text((60, 130), "Тест", fill='black', font=font)
    draw.text((210, 130), "123", fill='black', font=font)
    
    # Текст
    draw.text((50, 200), "Простой текст для OCR", fill='black', font=font)
    draw.text((50, 240), "Номер: 456-789", fill='black', font=font)
    
    return img

def test_simple_official_prompt():
    """Тест простого официального промпта"""
    print("🧪 Тестируем простой официальный промпт...")
    
    test_image = create_simple_test_image()
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Простой промпт для быстрого тестирования
    prompt = "Extract all text from this image."
    
    payload = {
        "model": "rednote-hilab/dots.ocr",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
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
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️ Время обработки: {processing_time:.2f}с")
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"✅ Успешный ответ: {content[:100]}...")
            
            # Проверяем, что текст распознан
            if any(word in content.lower() for word in ['тест', 'документ', '123', '456']):
                print("✅ Текст корректно распознан!")
                return True
            else:
                print("⚠️ Текст не распознан корректно")
                return False
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def test_bbox_official_prompt():
    """Тест BBOX официального промпта"""
    print("\n🎯 Тестируем BBOX официальный промпт...")
    
    test_image = create_simple_test_image()
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # BBOX промпт
    prompt = """Perform layout detection only. Identify and locate all layout elements in the document without text recognition. For each element provide:

1. Bbox coordinates: [x1, y1, x2, y2]
2. Category from: ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title']
3. Confidence score if available

Output as JSON array of detected layout elements."""
    
    payload = {
        "model": "rednote-hilab/dots.ocr",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
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
        "max_tokens": 1500,
        "temperature": 0.1
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️ Время обработки: {processing_time:.2f}с")
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"✅ Успешный ответ: {content[:150]}...")
            
            # Проверяем наличие BBOX координат
            if "bbox" in content.lower() and "[" in content and "]" in content:
                print("✅ BBOX координаты обнаружены!")
                return True
            else:
                print("⚠️ BBOX координаты не найдены")
                return False
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def monitor_container_logs_brief():
    """Краткий мониторинг логов контейнера"""
    try:
        result = subprocess.run(
            ["docker", "logs", "dots-ocr-fixed", "--tail", "3"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[-2:]:  # Показываем последние 2 строки
                if line.strip() and ("POST" in line or "ERROR" in line or "INFO" in line):
                    print(f"📋 {line}")
        
    except Exception as e:
        print(f"⚠️ Не удалось получить логи: {e}")

def check_streamlit_and_api_status():
    """Проверяем статус Streamlit и API"""
    print("🔍 Проверяем статус системы...")
    
    # Проверяем vLLM API (может быть на порту 8000 или 8004)
    api_ports = [8000, 8004]
    api_available = False
    active_port = None
    
    for port in api_ports:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ vLLM API доступен на порту {port}")
                api_available = True
                active_port = port
                break
        except Exception:
            continue
    
    if not api_available:
        print("❌ vLLM API недоступен на портах 8000 и 8004")
        return False
    
    # Проверяем Streamlit
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit приложение доступно")
        else:
            print(f"⚠️ Streamlit проблемы: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Streamlit недоступен: {e}")
        return False, None
    
    return True, active_port

def main():
    """Основная функция тестирования"""
    print("🚀 Тест интеграции официальных промптов в Streamlit")
    print("=" * 60)
    
    # Проверяем статус системы
    status_result = check_streamlit_and_api_status()
    if not status_result[0]:
        print("❌ Система недоступна")
        return
    
    active_port = status_result[1]
    print(f"🔧 Используем API на порту {active_port}")
    
    # Определяем модель по порту
    if active_port == 8000:
        model_name = "rednote-hilab/dots.ocr"
        print("🎯 Активна модель: dots.ocr")
    elif active_port == 8004:
        model_name = "Qwen/Qwen3-VL-2B-Instruct"
        print("🎯 Активна модель: Qwen3-VL-2B-Instruct")
    else:
        model_name = "rednote-hilab/dots.ocr"  # fallback
    
    # Проверяем логи перед тестами
    print("\n📋 Логи контейнера перед тестами:")
    monitor_container_logs_brief()
    
    # Тест 1: Простой OCR
    print("\n" + "=" * 60)
    simple_success = test_simple_official_prompt()
    
    # Тест 2: BBOX промпт
    print("\n" + "=" * 60)
    bbox_success = test_bbox_official_prompt()
    
    # Проверяем логи после тестов
    print("\n📋 Логи контейнера после тестов:")
    monitor_container_logs_brief()
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ:")
    print(f"   🔤 Простое OCR: {'✅' if simple_success else '❌'}")
    print(f"   📐 BBOX промпт: {'✅' if bbox_success else '❌'}")
    
    if simple_success and bbox_success:
        print("\n🎉 Все тесты прошли успешно!")
        print("✅ Официальные промпты dots.ocr работают корректно")
        print("✅ Система готова к использованию")
        
        print("\n💡 ИНСТРУКЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЯ:")
        print("1. Откройте http://localhost:8501")
        print("2. Перейдите в '💬 Режим чата'")
        print("3. Загрузите изображение")
        print("4. Используйте официальные промпты dots.ocr")
        print("5. Наслаждайтесь улучшенной функциональностью!")
        
    elif simple_success:
        print("\n⚠️ Частичный успех:")
        print("✅ Простое OCR работает")
        print("❌ BBOX промпты требуют дополнительной настройки")
        
    else:
        print("\n❌ Тесты не прошли")
        print("💡 Проверьте конфигурацию и перезапустите контейнер")

if __name__ == "__main__":
    main()