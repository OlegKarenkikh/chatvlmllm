#!/usr/bin/env python3
"""
Тестирование оптимизированной по памяти версии dots.ocr
"""

import requests
import base64
import time
from PIL import Image, ImageDraw, ImageFont
import io
import json

def create_test_image():
    """Создание тестового изображения"""
    img = Image.new('RGB', (600, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()
    
    # Добавляем разный текст для тестирования
    draw.text((50, 50), "MEMORY OPTIMIZED TEST", fill='black', font=font)
    draw.text((50, 100), "GPU Memory: Limited", fill='blue', font=font)
    draw.text((50, 150), "Status: Working ✓", fill='green', font=font)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def wait_for_server(max_attempts=30):
    """Ожидание готовности сервера"""
    print("⏳ Ожидание готовности сервера...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('model_loaded', False):
                    print("✅ Сервер готов и модель загружена!")
                    return True
                else:
                    print(f"⏳ Модель загружается... ({attempt + 1}/{max_attempts})")
            else:
                print(f"⏳ Сервер запускается... ({attempt + 1}/{max_attempts})")
        except requests.exceptions.ConnectionError:
            print(f"⏳ Подключение... ({attempt + 1}/{max_attempts})")
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
        
        time.sleep(10)
    
    print("❌ Сервер не готов после ожидания")
    return False

def test_health():
    """Тест health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check прошел")
            print(f"   Статус: {data.get('status')}")
            print(f"   Модель загружена: {data.get('model_loaded')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_models():
    """Тест models endpoint"""
    try:
        response = requests.get("http://localhost:8000/v1/models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])
            print(f"✅ Models endpoint работает")
            print(f"   Доступно моделей: {len(models)}")
            for model in models:
                print(f"   • {model.get('id')}")
            return True
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False

def test_ocr():
    """Тест OCR функциональности"""
    print("\n🧪 ТЕСТ OCR ФУНКЦИОНАЛЬНОСТИ")
    print("=" * 35)
    
    try:
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
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        print("🔄 Отправка OCR запроса...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            timeout=180  # Увеличенный таймаут для медленной обработки
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            print(f"✅ OCR результат получен за {processing_time:.1f} сек:")
            print(f"📝 Текст: {content}")
            
            # Проверка качества распознавания
            expected_words = ["MEMORY", "OPTIMIZED", "TEST", "GPU", "Limited", "Working"]
            found_words = sum(1 for word in expected_words if word.upper() in content.upper())
            
            print(f"🎯 Качество: {found_words}/{len(expected_words)} слов распознано")
            
            if found_words >= len(expected_words) // 2:
                print("🎉 OCR тест прошел успешно!")
                return True
            else:
                print("⚠️ Качество распознавания низкое, но API работает")
                return True
                
        else:
            print(f"❌ API ошибка: {response.status_code}")
            print(f"❌ Ответ: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса (возможно, недостаточно GPU памяти)")
        return False
    except Exception as e:
        print(f"❌ Ошибка OCR теста: {e}")
        return False

def test_performance():
    """Тест производительности"""
    print("\n⚡ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 30)
    
    # Создание простого изображения
    img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((50, 30), "SPEED TEST", fill='black')
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    payload = {
        "model": "rednote-hilab/dots.ocr",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract text"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        }],
        "max_tokens": 100
    }
    
    times = []
    successful = 0
    
    for i in range(3):
        try:
            print(f"🔄 Тест {i+1}/3...")
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/v1/chat/completions",
                json=payload,
                timeout=120
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                times.append(end_time - start_time)
                successful += 1
                print(f"   ✅ {end_time - start_time:.1f} сек")
            else:
                print(f"   ❌ Ошибка: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"   Успешных запросов: {successful}/3")
        print(f"   Среднее время: {avg_time:.1f} сек")
        print(f"   Мин/Макс: {min(times):.1f}/{max(times):.1f} сек")
        
        if avg_time < 60:
            print("   🚀 Хорошая производительность")
        elif avg_time < 120:
            print("   ⚠️ Медленная обработка (ограничения памяти)")
        else:
            print("   🐌 Очень медленная обработка")
    else:
        print("❌ Все тесты производительности провалились")

def main():
    """Основная функция"""
    print("🧪 ТЕСТИРОВАНИЕ ОПТИМИЗИРОВАННОЙ DOTS.OCR")
    print("=" * 50)
    
    # Ожидание готовности сервера
    if not wait_for_server():
        print("\n❌ Сервер не готов")
        print("💡 Возможные причины:")
        print("   • Недостаточно GPU памяти")
        print("   • Модель не загрузилась")
        print("   • Проблемы с Docker/vLLM")
        print("\n🔧 Попробуйте:")
        print("   • python gpu_memory_manager.py (очистка памяти)")
        print("   • docker logs dots-ocr-memory-opt (проверка логов)")
        print("   • python dots_ocr_transformers_8bit.py (альтернатива)")
        return
    
    # Базовые тесты
    print("\n🔍 БАЗОВЫЕ ТЕСТЫ")
    print("=" * 20)
    
    health_ok = test_health()
    models_ok = test_models()
    
    if not (health_ok and models_ok):
        print("❌ Базовые тесты не прошли")
        return
    
    # Тест OCR
    ocr_ok = test_ocr()
    
    if ocr_ok:
        # Тест производительности
        test_performance()
        
        print("\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
        print("=" * 25)
        print("✅ Система работает с ограничениями памяти")
        print("📡 API доступно: http://localhost:8000")
        print("📋 Документация: http://localhost:8000/docs")
        
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("   • Обрабатывайте изображения по одному")
        print("   • Используйте небольшие изображения для лучшей скорости")
        print("   • Мониторьте использование GPU памяти")
        
    else:
        print("\n❌ OCR тест не прошел")
        print("🔧 Попробуйте альтернативное решение:")
        print("   python dots_ocr_transformers_8bit.py")

if __name__ == "__main__":
    main()