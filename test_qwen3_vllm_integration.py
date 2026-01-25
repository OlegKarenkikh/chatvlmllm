#!/usr/bin/env python3
"""
Тест интеграции Qwen3-VL в vLLM режиме
"""

import requests
import time
import json
from PIL import Image
import base64
import io

def test_qwen3_vllm_integration():
    """Тестирование интеграции Qwen3-VL в vLLM"""
    
    print("🚀 Тестирование интеграции Qwen3-VL в vLLM режиме")
    print("=" * 60)
    
    # Конфигурация endpoints
    endpoints = {
        "dots.ocr": "http://localhost:8000",
        "Qwen2-VL-2B": "http://localhost:8001", 
        "Qwen3-VL-2B": "http://localhost:8004",
        "Phi-3.5-Vision": "http://localhost:8002",
        "Qwen2-VL-7B": "http://localhost:8003"
    }
    
    models = {
        "dots.ocr": "rednote-hilab/dots.ocr",
        "Qwen2-VL-2B": "Qwen/Qwen2-VL-2B-Instruct",
        "Qwen3-VL-2B": "Qwen/Qwen3-VL-2B-Instruct",
        "Phi-3.5-Vision": "microsoft/Phi-3.5-vision-instruct",
        "Qwen2-VL-7B": "Qwen/Qwen2-VL-7B-Instruct"
    }
    
    results = {}
    
    # 1. Проверка доступности всех endpoints
    print("\n1️⃣ Проверка доступности vLLM серверов:")
    print("-" * 40)
    
    available_endpoints = {}
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(f"{endpoint}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {endpoint} - ДОСТУПЕН")
                available_endpoints[name] = endpoint
                
                # Получаем информацию о модели
                models_response = requests.get(f"{endpoint}/v1/models", timeout=5)
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    for model in models_data.get("data", []):
                        print(f"   📋 Модель: {model['id']}")
                        print(f"   🔢 Макс. токенов: {model.get('max_model_len', 'N/A')}")
                        break
            else:
                print(f"❌ {name}: {endpoint} - НЕДОСТУПЕН (код: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: {endpoint} - ОШИБКА ({str(e)[:50]}...)")
    
    if not available_endpoints:
        print("\n❌ Нет доступных vLLM серверов!")
        print("💡 Запустите контейнеры: docker-compose -f docker-compose-vllm.yml up -d")
        return
    
    # 2. Создание тестового изображения
    print(f"\n2️⃣ Создание тестового изображения:")
    print("-" * 40)
    
    # Создаем простое изображение с текстом
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Пытаемся использовать системный шрифт
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Если не найден, используем стандартный
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Qwen3-VL Test", fill='black', font=font)
    draw.text((50, 100), "Hello World!", fill='blue', font=font)
    draw.text((50, 150), "Тест на русском", fill='red', font=font)
    
    # Сохраняем изображение
    test_image_path = "test_qwen3_vllm_integration.png"
    img.save(test_image_path)
    print(f"✅ Тестовое изображение создано: {test_image_path}")
    
    # Конвертируем в base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 3. Тестирование каждого доступного endpoint
    print(f"\n3️⃣ Тестирование OCR через доступные модели:")
    print("-" * 40)
    
    test_prompt = "Extract all text from this image"
    
    for name, endpoint in available_endpoints.items():
        print(f"\n🔄 Тестирование {name}...")
        
        model_name = models[name]
        
        payload = {
            "model": model_name,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": test_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 1024,
            "temperature": 0.1
        }
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{endpoint}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                
                print(f"✅ {name} - УСПЕШНО")
                print(f"   ⏱️ Время: {processing_time:.1f} сек")
                print(f"   🔢 Токенов: {tokens_used}")
                print(f"   📄 Результат: {content[:100]}...")
                
                results[name] = {
                    "status": "success",
                    "processing_time": processing_time,
                    "tokens_used": tokens_used,
                    "content": content,
                    "endpoint": endpoint,
                    "model": model_name
                }
                
                # Особое внимание к Qwen3-VL
                if name == "Qwen3-VL-2B":
                    print(f"🎯 QWEN3-VL РЕЗУЛЬТАТ:")
                    print(f"   📋 Полный текст: {content}")
                    
            else:
                error_text = response.text
                print(f"❌ {name} - ОШИБКА API (код: {response.status_code})")
                print(f"   📄 Ответ: {error_text[:200]}...")
                
                results[name] = {
                    "status": "api_error",
                    "error_code": response.status_code,
                    "error_text": error_text[:500],
                    "endpoint": endpoint
                }
                
        except Exception as e:
            print(f"❌ {name} - ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
            results[name] = {
                "status": "connection_error",
                "error": str(e),
                "endpoint": endpoint
            }
    
    # 4. Сводка результатов
    print(f"\n4️⃣ Сводка результатов:")
    print("=" * 60)
    
    successful_models = [name for name, result in results.items() if result["status"] == "success"]
    failed_models = [name for name, result in results.items() if result["status"] != "success"]
    
    print(f"✅ Успешно работают: {len(successful_models)} моделей")
    for name in successful_models:
        result = results[name]
        print(f"   🟢 {name}: {result['processing_time']:.1f}s, {result['tokens_used']} токенов")
    
    if failed_models:
        print(f"\n❌ Не работают: {len(failed_models)} моделей")
        for name in failed_models:
            result = results[name]
            print(f"   🔴 {name}: {result['status']}")
    
    # Проверяем Qwen3-VL специально
    if "Qwen3-VL-2B" in successful_models:
        print(f"\n🎯 QWEN3-VL ИНТЕГРАЦИЯ: ✅ УСПЕШНА")
        qwen3_result = results["Qwen3-VL-2B"]
        print(f"   🌐 Endpoint: {qwen3_result['endpoint']}")
        print(f"   🤖 Модель: {qwen3_result['model']}")
        print(f"   ⏱️ Время обработки: {qwen3_result['processing_time']:.1f} сек")
        print(f"   📄 Качество OCR: {'ХОРОШЕЕ' if len(qwen3_result['content']) > 10 else 'ПЛОХОЕ'}")
    else:
        print(f"\n🎯 QWEN3-VL ИНТЕГРАЦИЯ: ❌ НЕ РАБОТАЕТ")
        if "Qwen3-VL-2B" in results:
            qwen3_result = results["Qwen3-VL-2B"]
            print(f"   ❌ Статус: {qwen3_result['status']}")
            if "error" in qwen3_result:
                print(f"   📄 Ошибка: {qwen3_result['error']}")
    
    # 5. Сохранение результатов
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"qwen3_vllm_integration_test_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "test_type": "qwen3_vllm_integration",
            "available_endpoints": len(available_endpoints),
            "total_endpoints": len(endpoints),
            "successful_models": successful_models,
            "failed_models": failed_models,
            "detailed_results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены: {results_file}")
    
    # 6. Рекомендации
    print(f"\n6️⃣ Рекомендации:")
    print("-" * 40)
    
    if "Qwen3-VL-2B" in successful_models:
        print("✅ Qwen3-VL успешно интегрирован в vLLM режим")
        print("💡 Можно перезапускать приложение и использовать Qwen3-VL")
        print("🚀 Команда запуска: streamlit run app.py")
    else:
        print("❌ Qwen3-VL не работает в vLLM режиме")
        print("💡 Проверьте:")
        print("   1. Запущен ли контейнер: docker ps | grep qwen3")
        print("   2. Доступен ли порт 8004: curl http://localhost:8004/health")
        print("   3. Логи контейнера: docker logs qwen-qwen3-vl-2b-instruct-vllm")
    
    return results

if __name__ == "__main__":
    test_qwen3_vllm_integration()