#!/usr/bin/env python3
"""
Тестирование оптимизации токенов vLLM
"""

import requests
import time
import json
from datetime import datetime

def test_vllm_optimization():
    """Тестирование оптимизированной конфигурации vLLM"""
    
    print("🧪 ТЕСТИРОВАНИЕ ОПТИМИЗАЦИИ vLLM ТОКЕНОВ")
    print("=" * 50)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. Проверка здоровья сервера
    print("\n1️⃣ Проверка здоровья сервера...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ vLLM сервер работает")
        else:
            print(f"❌ Сервер недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    # 2. Проверка моделей и лимитов токенов
    print("\n2️⃣ Проверка лимитов токенов...")
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            
            for model in models_data.get("data", []):
                model_id = model["id"]
                max_tokens = model.get("max_model_len", "неизвестно")
                created = model.get("created", "неизвестно")
                
                print(f"📊 Модель: {model_id}")
                print(f"   📏 Лимит токенов: {max_tokens:,}")
                print(f"   📅 Создана: {created}")
                
                # Проверяем, что лимит увеличен
                if max_tokens == 8192:
                    print("   ✅ ОПТИМИЗАЦИЯ ПРИМЕНЕНА! (8,192 токенов)")
                    optimization_applied = True
                elif max_tokens == 1024:
                    print("   ⚠️ Старый лимит (1,024 токенов)")
                    optimization_applied = False
                else:
                    print(f"   ❓ Неожиданный лимит: {max_tokens}")
                    optimization_applied = False
                
                return optimization_applied
        else:
            print(f"❌ Ошибка получения моделей: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки моделей: {e}")
        return False

def test_token_limits():
    """Тестирование различных лимитов токенов"""
    
    print("\n3️⃣ Тестирование различных лимитов токенов...")
    
    base_url = "http://localhost:8000"
    
    # Тестовые запросы с разными лимитами токенов
    test_cases = [
        {"max_tokens": 512, "description": "Малый лимит (512)"},
        {"max_tokens": 1024, "description": "Старый лимит (1,024)"},
        {"max_tokens": 2048, "description": "Средний лимит (2,048)"},
        {"max_tokens": 4096, "description": "Большой лимит (4,096)"},
        {"max_tokens": 8192, "description": "Максимальный лимит (8,192)"},
    ]
    
    # Простой тестовый промпт
    test_prompt = "Describe what you see in this image in detail."
    
    # Создаем простое тестовое изображение (белый квадрат с текстом)
    import base64
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Создаем тестовое изображение
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Добавляем текст
    try:
        # Пытаемся использовать системный шрифт
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        # Если не найден, используем стандартный
        font = ImageFont.load_default()
    
    draw.text((50, 80), "TEST IMAGE FOR vLLM OPTIMIZATION", fill='black', font=font)
    
    # Конвертируем в base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    results = []
    
    for test_case in test_cases:
        max_tokens = test_case["max_tokens"]
        description = test_case["description"]
        
        print(f"\n   🧪 Тестирование: {description}")
        
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": test_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": max_tokens,
            "temperature": 0.1
        }
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                
                print(f"      ✅ Успех: {processing_time:.1f}с, токенов: {tokens_used}")
                
                results.append({
                    "max_tokens": max_tokens,
                    "success": True,
                    "processing_time": processing_time,
                    "tokens_used": tokens_used,
                    "response_length": len(content)
                })
            else:
                print(f"      ❌ Ошибка: {response.status_code}")
                print(f"         Ответ: {response.text[:100]}...")
                
                results.append({
                    "max_tokens": max_tokens,
                    "success": False,
                    "error": response.status_code,
                    "error_text": response.text[:200]
                })
                
        except Exception as e:
            print(f"      ❌ Исключение: {e}")
            results.append({
                "max_tokens": max_tokens,
                "success": False,
                "error": "exception",
                "error_text": str(e)
            })
    
    return results

def generate_test_report(optimization_applied, test_results):
    """Генерация отчета о тестировании"""
    
    print("\n" + "=" * 50)
    print("📊 ОТЧЕТ О ТЕСТИРОВАНИИ ОПТИМИЗАЦИИ")
    print("=" * 50)
    
    # Статус оптимизации
    if optimization_applied:
        print("✅ ОПТИМИЗАЦИЯ ПРИМЕНЕНА УСПЕШНО!")
        print("   📏 Лимит токенов увеличен до 8,192")
    else:
        print("❌ ОПТИМИЗАЦИЯ НЕ ПРИМЕНЕНА")
        print("   📏 Лимит токенов остался 1,024")
    
    # Результаты тестирования
    print(f"\n📈 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ТОКЕНОВ:")
    
    successful_tests = 0
    failed_tests = 0
    
    for result in test_results:
        max_tokens = result["max_tokens"]
        
        if result["success"]:
            successful_tests += 1
            processing_time = result["processing_time"]
            tokens_used = result["tokens_used"]
            response_length = result["response_length"]
            
            print(f"   ✅ {max_tokens:,} токенов: {processing_time:.1f}с, использовано {tokens_used}, длина {response_length}")
        else:
            failed_tests += 1
            error = result.get("error", "unknown")
            print(f"   ❌ {max_tokens:,} токенов: ОШИБКА ({error})")
    
    # Сводка
    print(f"\n📊 СВОДКА ТЕСТИРОВАНИЯ:")
    print(f"   ✅ Успешных тестов: {successful_tests}")
    print(f"   ❌ Неудачных тестов: {failed_tests}")
    print(f"   📈 Процент успеха: {(successful_tests/(successful_tests+failed_tests)*100):.1f}%")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    
    if optimization_applied and successful_tests >= 4:
        print("   🎉 ОПТИМИЗАЦИЯ РАБОТАЕТ ОТЛИЧНО!")
        print("   ✅ Все лимиты токенов поддерживаются")
        print("   🚀 Система готова к продуктивному использованию")
    elif optimization_applied and successful_tests >= 2:
        print("   ⚠️ Оптимизация частично работает")
        print("   💡 Проверьте логи для высоких лимитов токенов")
    elif not optimization_applied:
        print("   🔄 НЕОБХОДИМО ПРИМЕНИТЬ ОПТИМИЗАЦИЮ")
        print("   💡 Запустите: restart_vllm_optimized.bat")
    else:
        print("   ❌ Обнаружены проблемы с сервером")
        print("   💡 Проверьте логи: docker-compose logs")
    
    # Сохранение отчета
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "optimization_applied": optimization_applied,
        "test_results": test_results,
        "summary": {
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests/(successful_tests+failed_tests)*100) if (successful_tests+failed_tests) > 0 else 0
        }
    }
    
    with open("vllm_optimization_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Подробный отчет сохранен: vllm_optimization_test_report.json")

def main():
    """Главная функция тестирования"""
    
    # Проверка оптимизации
    optimization_applied = test_vllm_optimization()
    
    if optimization_applied is False:
        print("\n❌ Сервер недоступен или оптимизация не применена")
        print("💡 Убедитесь, что vLLM сервер запущен и оптимизирован")
        return
    
    # Тестирование лимитов токенов
    test_results = test_token_limits()
    
    # Генерация отчета
    generate_test_report(optimization_applied, test_results)

if __name__ == "__main__":
    main()