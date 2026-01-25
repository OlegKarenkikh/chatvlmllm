#!/usr/bin/env python3
"""
Проверка доступности модели Qwen3-VL в vLLM
"""

import requests
import json
import time

def check_qwen3_vllm():
    """Проверка доступности Qwen3-VL в vLLM"""
    
    print("🔍 ПРОВЕРКА ДОСТУПНОСТИ QWEN3-VL В vLLM")
    print("=" * 50)
    
    # Endpoint для Qwen3-VL
    qwen3_endpoint = "http://localhost:8004"
    model_name = "Qwen/Qwen3-VL-2B-Instruct"
    
    # 1. Проверка health endpoint
    print(f"1️⃣ Проверка health endpoint: {qwen3_endpoint}/health")
    try:
        response = requests.get(f"{qwen3_endpoint}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check: OK")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # 2. Проверка доступных моделей
    print(f"\n2️⃣ Проверка доступных моделей: {qwen3_endpoint}/v1/models")
    try:
        response = requests.get(f"{qwen3_endpoint}/v1/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            print("✅ Models endpoint: OK")
            
            # Ищем нашу модель
            found_model = None
            for model in models_data.get("data", []):
                if model["id"] == model_name:
                    found_model = model
                    break
            
            if found_model:
                print(f"✅ Модель найдена: {model_name}")
                print(f"   📏 Max tokens: {found_model.get('max_model_len', 'N/A')}")
                print(f"   🏷️ Object: {found_model.get('object', 'N/A')}")
            else:
                print(f"❌ Модель {model_name} не найдена")
                print("📋 Доступные модели:")
                for model in models_data.get("data", []):
                    print(f"   - {model['id']}")
                return False
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False
    
    # 3. Тест простого запроса
    print(f"\n3️⃣ Тест простого запроса к модели")
    try:
        test_payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": "Привет! Как дела?"
                }
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        response = requests.post(
            f"{qwen3_endpoint}/v1/chat/completions",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"]
                print("✅ Тест запроса: OK")
                print(f"   💬 Ответ: {answer[:100]}...")
                print(f"   🔢 Tokens: {result.get('usage', {}).get('total_tokens', 'N/A')}")
            else:
                print("❌ Тест запроса: Нет ответа в результате")
                return False
        else:
            print(f"❌ Тест запроса failed: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Тест запроса error: {e}")
        return False
    
    print(f"\n🎉 QWEN3-VL ГОТОВ К ИСПОЛЬЗОВАНИЮ!")
    print("=" * 50)
    print(f"📍 Endpoint: {qwen3_endpoint}")
    print(f"🏷️ Model: {model_name}")
    print(f"🚀 Status: Полностью функционален")
    
    return True

def check_vllm_adapter():
    """Проверка работы VLLMStreamlitAdapter с Qwen3"""
    
    print(f"\n🔧 ПРОВЕРКА VLLM ADAPTER")
    print("=" * 30)
    
    try:
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        
        # Создаем адаптер
        adapter = VLLMStreamlitAdapter()
        
        print(f"✅ VLLMStreamlitAdapter создан")
        print(f"📋 Доступные модели: {len(adapter.available_models)}")
        
        for model in adapter.available_models:
            endpoint = adapter.get_endpoint_for_model(model)
            max_tokens = adapter.get_model_max_tokens(model)
            print(f"   🚀 {model.split('/')[-1]}: {endpoint} (max: {max_tokens})")
        
        # Проверяем Qwen3 конкретно
        qwen3_model = "Qwen/Qwen3-VL-2B-Instruct"
        if qwen3_model in adapter.available_models:
            print(f"\n✅ Qwen3-VL доступен через адаптер!")
            endpoint = adapter.get_endpoint_for_model(qwen3_model)
            max_tokens = adapter.get_model_max_tokens(qwen3_model)
            print(f"   📍 Endpoint: {endpoint}")
            print(f"   🔢 Max tokens: {max_tokens}")
        else:
            print(f"\n❌ Qwen3-VL НЕ доступен через адаптер")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка VLLMStreamlitAdapter: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ПРОВЕРКА ДОСТУПНОСТИ QWEN3-VL ДЛЯ vLLM")
    print("=" * 60)
    
    # Проверяем прямое подключение к vLLM
    vllm_ok = check_qwen3_vllm()
    
    # Проверяем работу через адаптер
    adapter_ok = check_vllm_adapter()
    
    print(f"\n📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("=" * 30)
    print(f"vLLM сервер: {'✅ OK' if vllm_ok else '❌ FAIL'}")
    print(f"Streamlit адаптер: {'✅ OK' if adapter_ok else '❌ FAIL'}")
    
    if vllm_ok and adapter_ok:
        print(f"\n🎊 ВСЕ ГОТОВО!")
        print("Теперь в приложении:")
        print("1. Выберите 'vLLM (Рекомендуется)' в режиме выполнения")
        print("2. Выберите 'Qwen3-VL-2B-Instruct' в списке моделей")
        print("3. Используйте модель для OCR и чата!")
    else:
        print(f"\n❌ ЕСТЬ ПРОБЛЕМЫ - проверьте логи выше")