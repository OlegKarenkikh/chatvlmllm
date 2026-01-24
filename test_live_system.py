#!/usr/bin/env python3
"""
Тест живой системы ChatVLMLLM
"""

import requests
import time
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import json

def create_test_image():
    """Создаем тестовое изображение"""
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 20), "ЖИВОЙ ТЕСТ СИСТЕМЫ", fill='black', font=font)
    draw.text((20, 50), "Номер: 987654321", fill='black', font=font)
    draw.text((20, 80), "Дата: 24.01.2026", fill='black', font=font)
    draw.text((20, 110), "Статус: РАБОТАЕТ", fill='black', font=font)
    draw.text((20, 140), "GPU: RTX 5070 Ti", fill='black', font=font)
    
    return img

def image_to_base64(image):
    """Конвертирует PIL изображение в base64"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def test_api_health():
    """Тестирует health endpoint"""
    print("🔍 Тестируем API health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API здоров!")
            print(f"   📊 Модели загружены: {data.get('models_loaded', 0)}")
            print(f"   💾 VRAM: {data.get('vram_used_gb', 0):.2f}GB")
            print(f"   🔧 Доступные модели: {data.get('loaded_models', [])}")
            return True
        else:
            print(f"❌ API ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return False

def test_api_models():
    """Тестирует список моделей"""
    print("\n📋 Получаем список моделей...")
    try:
        response = requests.get("http://localhost:8000/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print("✅ Модели получены:")
            for model in models:
                print(f"   - {model}")
            return models
        else:
            print(f"❌ Ошибка получения моделей: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def test_api_ocr():
    """Тестирует OCR через API"""
    print("\n🔍 Тестируем OCR через API...")
    
    # Создаем тестовое изображение
    image = create_test_image()
    
    # Сохраняем во временный файл
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        image.save(tmp_file.name, format='PNG')
        tmp_filename = tmp_file.name
    
    try:
        print("📤 Отправляем запрос OCR...")
        start_time = time.time()
        
        # Правильный формат для API - multipart/form-data
        with open(tmp_filename, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            data = {'model': 'qwen_vl_2b'}  # Используем основную модель
            
            response = requests.post(
                "http://localhost:8000/ocr", 
                files=files,
                data=data,
                timeout=120  # Увеличиваем таймаут для загрузки модели
            )
        
        process_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ OCR успешно! Время: {process_time:.2f}s")
            print(f"📝 Результат: {result.get('text', 'No text')}")
            print(f"🎯 Модель: {result.get('model', 'Unknown')}")
            print(f"⚡ Время обработки: {result.get('processing_time', 0):.2f}s")
            
            # Проверяем качество
            keywords = ["ЖИВОЙ", "ТЕСТ", "987654321", "24.01.2026", "РАБОТАЕТ"]
            text = result.get('text', '').upper()
            found = sum(1 for kw in keywords if kw in text)
            quality = (found / len(keywords)) * 100
            print(f"🎯 Качество: {found}/{len(keywords)} ({quality:.0f}%)")
            
            return True
        else:
            print(f"❌ OCR ошибка: {response.status_code}")
            print(f"📝 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка OCR: {e}")
        return False
    finally:
        # Удаляем временный файл
        try:
            import os
            os.unlink(tmp_filename)
        except:
            pass

def test_streamlit_access():
    """Тестирует доступность Streamlit"""
    print("\n🌐 Тестируем Streamlit интерфейс...")
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            print("✅ Streamlit доступен!")
            print("🌐 URL: http://localhost:8501")
            return True
        else:
            print(f"❌ Streamlit ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Streamlit: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТ ЖИВОЙ СИСТЕМЫ ChatVLMLLM")
    print("=" * 50)
    
    results = {
        "api_health": False,
        "api_models": False,
        "api_ocr": False,
        "streamlit": False
    }
    
    # Тестируем компоненты
    results["api_health"] = test_api_health()
    
    if results["api_health"]:
        models = test_api_models()
        results["api_models"] = len(models) > 0
        
        if results["api_models"]:
            results["api_ocr"] = test_api_ocr()
    
    results["streamlit"] = test_streamlit_access()
    
    # Итоговый отчет
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ ПРОШЕЛ" if passed else "❌ ПРОВАЛЕН"
        print(f"{test_name:15} | {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n🏆 РЕЗУЛЬТАТ: {passed_tests}/{total_tests} тестов прошли ({success_rate:.0f}%)")
    
    if success_rate == 100:
        print("🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ ОТЛИЧНО!")
        print("✅ Система готова к использованию")
    elif success_rate >= 75:
        print("👍 Система в основном работает")
        print("⚠️ Есть незначительные проблемы")
    else:
        print("⚠️ Есть серьезные проблемы с системой")
        print("🔧 Требуется диагностика")
    
    print(f"\n🌐 Веб-интерфейс: http://localhost:8501")
    print(f"🚀 API документация: http://localhost:8000/docs")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)